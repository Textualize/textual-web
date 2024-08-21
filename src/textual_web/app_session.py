from __future__ import annotations

import asyncio
from asyncio import StreamReader, StreamWriter, IncompleteReadError
from asyncio.subprocess import Process
from enum import Enum, auto
import io
import logging
import json
import logging
import os
from time import monotonic
from datetime import timedelta
from pathlib import Path

from importlib_metadata import version

import rich.repr

from . import constants
from .session import Session, SessionConnector
from .types import Meta, SessionID


log = logging.getLogger("textual-web")


class ProcessState(Enum):
    """The state of a process."""

    PENDING = auto()
    RUNNING = auto()
    CLOSING = auto()
    CLOSED = auto()

    def __repr__(self) -> str:
        return self.name


@rich.repr.auto(angular=True)
class AppSession(Session):
    """Runs a single app process."""

    def __init__(
        self,
        working_directory: Path,
        command: str,
        session_id: SessionID,
        devtools: bool = False,
    ) -> None:
        self.working_directory = working_directory
        self.command = command
        self.session_id = session_id
        self.devtools = devtools
        self.start_time: float | None = None
        self.end_time: float | None = None
        self._process: Process | None = None
        self._task: asyncio.Task | None = None

        super().__init__()
        self._state = ProcessState.PENDING

    @property
    def process(self) -> Process:
        """The asyncio (sub)process"""
        assert self._process is not None
        return self._process

    @property
    def stdin(self) -> StreamWriter:
        """The processes stdin."""
        assert self._process is not None
        assert self._process.stdin is not None
        return self._process.stdin

    @property
    def stdout(self) -> StreamReader:
        """The process' stdout."""
        assert self._process is not None
        assert self._process.stdout is not None
        return self._process.stdout

    @property
    def stderr(self) -> StreamReader:
        """The process' stderr."""
        assert self._process is not None
        assert self._process.stderr is not None
        return self._process.stderr

    @property
    def task(self) -> asyncio.Task:
        """Session task."""
        assert self._task is not None
        return self._task

    @property
    def state(self) -> ProcessState:
        """Current running state."""
        return self._state

    @state.setter
    def state(self, state: ProcessState) -> None:
        self._state = state
        run_time = self.run_time
        log.debug(
            "%r state=%r run_time=%s",
            self,
            self.state,
            "0" if run_time is None else timedelta(seconds=int(run_time)),
        )

    @property
    def run_time(self) -> float | None:
        """Time process was running, or `None` if it hasn't started."""
        if self.end_time is not None:
            assert self.start_time is not None
            return self.end_time - self.start_time
        elif self.start_time is not None:
            return monotonic() - self.start_time
        else:
            return None

    def __rich_repr__(self) -> rich.repr.Result:
        yield self.command
        yield "id", self.session_id
        if self._process is not None:
            yield "returncode", self._process.returncode, None

    async def open(self, width: int = 80, height: int = 24) -> None:
        """Open the process."""
        environment = dict(os.environ.copy())
        environment["TEXTUAL_DRIVER"] = "textual.drivers.web_driver:WebDriver"
        environment["TEXTUAL_FPS"] = "60"
        environment["TEXTUAL_COLOR_SYSTEM"] = "truecolor"
        environment["TERM_PROGRAM"] = "textual-web"
        environment["TERM_PROGRAM_VERSION"] = version("textual-web")
        environment["COLUMNS"] = str(width)
        environment["ROWS"] = str(height)
        if self.devtools:
            environment["TEXTUAL"] = "debug,devtools"
            environment["TEXTUAL_LOG"] = "textual.log"

        cwd = os.getcwd()
        os.chdir(str(self.working_directory))
        try:
            self._process = await asyncio.create_subprocess_shell(
                self.command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=environment,
            )
        finally:
            os.chdir(cwd)
        await self.set_terminal_size(width, height)
        log.debug("opened %r; %r", self.command, self._process)
        self.start_time = monotonic()

    async def start(self, connector: SessionConnector) -> asyncio.Task:
        """Start a task to run the process."""
        self._connector = connector
        assert self._task is None
        self._task = asyncio.create_task(self.run())
        return self._task

    async def close(self) -> None:
        """Close the process."""
        self.state = ProcessState.CLOSING
        await self.send_meta({"type": "quit"})

    async def wait(self) -> None:
        """Wait for the process to finish (call close first)."""
        if self._task:
            await self._task
            self._task = None

    async def set_terminal_size(self, width: int, height: int) -> None:
        """Set the terminal size for the process.

        Args:
            width: Width in cells.
            height: Height in cells.
        """
        await self.send_meta(
            {
                "type": "resize",
                "width": width,
                "height": height,
            }
        )

    async def run(self) -> None:
        """This loop reads stdout from the process and relays it through the websocket."""

        self.state = ProcessState.RUNNING

        META = b"M"
        DATA = b"D"
        BINARY_ENCODED = b"P"

        stderr_data = io.BytesIO()

        async def read_stderr() -> None:
            """Task to read stderr."""
            try:
                while True:
                    data = await self.stderr.read(1024 * 4)
                    if not data:
                        break
                    stderr_data.write(data)
            except asyncio.CancelledError:
                pass

        stderr_task = asyncio.create_task(read_stderr())
        readexactly = self.stdout.readexactly
        from_bytes = int.from_bytes

        on_data = self._connector.on_data
        on_meta = self._connector.on_meta
        on_binary_encoded_message = self._connector.on_binary_encoded_message
        try:
            ready = False
            for _ in range(10):
                line = await self.stdout.readline()
                if not line:
                    break
                if line == b"__GANGLION__\n":
                    ready = True
                    break
            if ready:
                while True:
                    type_bytes = await readexactly(1)
                    size_bytes = await readexactly(4)
                    size = from_bytes(size_bytes, "big")
                    payload = await readexactly(size)
                    if type_bytes == DATA:
                        await on_data(payload)
                    elif type_bytes == META:
                        meta_data = json.loads(payload)
                        meta_type = meta_data.get("type")
                        if meta_type in {"exit", "blur", "focus"}:
                            await self.send_meta({"type": meta_type})
                        else:
                            await on_meta(json.loads(payload))
                    elif type_bytes == BINARY_ENCODED:
                        await on_binary_encoded_message(payload)

        except IncompleteReadError:
            # Incomplete read means that the stream was closed
            pass
        except asyncio.CancelledError:
            pass
        finally:
            stderr_task.cancel()
            await stderr_task

        self.end_time = monotonic()
        self.state = ProcessState.CLOSED

        stderr_message = stderr_data.getvalue().decode("utf-8", errors="replace")
        if self._process is not None and self._process.returncode != 0:
            if constants.DEBUG and stderr_message:
                log.warning(stderr_message)

        await self._connector.on_close()

    @classmethod
    def encode_packet(cls, packet_type: bytes, payload: bytes) -> bytes:
        """Encode a packet.

        Args:
            packet_type: The packet type (b"D" for data or b"M" for meta)
            payload: The payload.

        Returns:
            Data as bytes.
        """
        return b"%s%s%s" % (packet_type, len(payload).to_bytes(4, "big"), payload)

    async def send_bytes(self, data: bytes) -> bool:
        """Send bytes to process.

        Args:
            data: Data to send.

        Returns:
            True if the data was sent, otherwise False.
        """
        stdin = self.stdin
        try:
            stdin.write(self.encode_packet(b"D", data))
        except RuntimeError:
            return False
        await stdin.drain()
        return True

    async def send_meta(self, data: Meta) -> bool:
        """Send meta information to process.

        Args:
            data: Meta dict to send.

        Returns:
            True if the data was sent, otherwise False.
        """
        stdin = self.stdin
        data_bytes = json.dumps(data).encode("utf-8")
        try:
            stdin.write(self.encode_packet(b"M", data_bytes))
        except RuntimeError:
            return False
        await stdin.drain()
        return True
