from __future__ import annotations

import asyncio
import array
import fcntl
import logging
import os
import pty
import signal
import termios

from importlib_metadata import version
import rich.repr

from .poller import Poller
from .session import Session, SessionConnector
from .types import Meta, SessionID

log = logging.getLogger("textual-web")

@rich.repr.auto
class TerminalSession(Session):
    """A session that manages a terminal."""

    def __init__(
        self,
        poller: Poller,
        session_id: SessionID,
        command: str,
    ) -> None:
        self.poller = poller
        self.session_id = session_id
        self.command = command or os.environ.get("SHELL", "sh")
        self.master_fd: int | None = None
        self.pid: int | None = None
        self._task: asyncio.Task | None = None
        super().__init__()

    def __rich_repr__(self) -> rich.repr.Result:
        yield "session_id", self.session_id
        yield "command", self.command

    async def open(self, width: int = 80, height: int = 24) -> None:
        pid, master_fd = pty.fork()
        self.pid = pid
        self.master_fd = master_fd
        if pid == pty.CHILD:
            os.environ["TERM_PROGRAM"] = "textual-web"
            os.environ["TERM_PROGRAM_VERSION"] = version("textual-web")
            argv = [self.command]
            try:
                os.execlp(argv[0], *argv)  ## Exits the app
            except Exception:
                os._exit(0)
        self._set_terminal_size(width, height)

    def _set_terminal_size(self, width: int, height: int) -> None:
        buf = array.array("h", [height, width, 0, 0])
        assert self.master_fd is not None
        fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, buf)

    async def set_terminal_size(self, width: int, height: int) -> None:
        self._set_terminal_size(width, height)

    async def start(self, connector: SessionConnector) -> asyncio.Task:
        self._connector = connector
        assert self.master_fd is not None
        assert self._task is None
        self._task = self._task = asyncio.create_task(self.run())
        return self._task

    async def run(self) -> None:
        assert self.master_fd is not None
        queue = self.poller.add_file(self.master_fd)
        on_data = self._connector.on_data
        on_close = self._connector.on_close
        try:
            while True:
                data = await queue.get() or None
                if data is None:
                    break
                await on_data(data)
        except Exception:
            log.exception("error in terminal.run")
        finally:
            await on_close()
            os.close(self.master_fd)
            self.poller.remove_file(self.master_fd)
            self.master_fd = None

    async def send_bytes(self, data: bytes) -> bool:
        if self.master_fd is None:
            return False
        await self.poller.write(self.master_fd, data)
        return True

    async def send_meta(self, data: Meta) -> bool:
        return True

    async def close(self) -> None:
        if self.pid is not None:
            os.kill(self.pid, signal.SIGHUP)

    async def wait(self) -> None:
        if self._task is not None:
            await self._task
