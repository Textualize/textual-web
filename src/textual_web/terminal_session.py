from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque
import asyncio
import array
import fcntl
import logging
import os
import pty
import signal
import select
import termios
from threading import Thread, Event

import rich.repr

from .session import Session, SessionConnector
from .types import Meta, SessionID

log = logging.getLogger("textual-web")


@dataclass
class Write:
    """Data in a write queue."""

    data: bytes
    position: int = 0
    done_event: asyncio.Event = field(default_factory=asyncio.Event)


READABLE_EVENTS = select.POLLIN | select.POLLPRI
WRITEABLE_EVENTS = select.POLLOUT
ERROR_EVENTS = select.POLLERR | select.POLLHUP


class Poller(Thread):
    """A thread which reads from file descriptors and posts read data to a queue."""

    def __init__(self) -> None:
        super().__init__()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._poll = select.poll()
        self._read_queues: dict[int, asyncio.Queue[bytes | None]] = {}
        self._write_queues: dict[int, deque[Write]] = {}
        self._exit_event = Event()

    def add_file(self, file_descriptor: int) -> asyncio.Queue:
        """Add a file descriptor to the poller.

        Args:
            file_descriptor: File descriptor.

        Returns:
            Async queue.
        """
        self._poll.register(
            file_descriptor, READABLE_EVENTS | WRITEABLE_EVENTS | ERROR_EVENTS
        )
        queue = self._read_queues[file_descriptor] = asyncio.Queue()
        return queue

    def remove_file(self, file_descriptor: int) -> None:
        """Remove a file descriptor from the poller.

        Args:
            file_descriptor: File descriptor.
        """
        self._read_queues.pop(file_descriptor, None)
        self._write_queues.pop(file_descriptor, None)

    async def write(self, file_descriptor: int, data: bytes) -> None:
        """Write data to a file descriptor.

        Args:
            file_descriptor: File descriptor.
            data: Data to write.
        """
        if file_descriptor not in self._write_queues:
            self._write_queues[file_descriptor] = deque()
        new_write = Write(data)
        self._write_queues[file_descriptor].append(new_write)
        self._poll.register(
            file_descriptor, READABLE_EVENTS | WRITEABLE_EVENTS | ERROR_EVENTS
        )
        await new_write.done_event.wait()

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Set the asyncio loop.

        Args:
            loop: Async loop.
        """
        self._loop = loop

    def run(self) -> None:
        """Run the Poller thread."""
        readable_events = READABLE_EVENTS
        writeable_events = WRITEABLE_EVENTS
        error_events = ERROR_EVENTS
        loop = self._loop
        assert loop is not None
        while not self._exit_event.is_set():
            poll_result = self._poll.poll(1000)
            for file_descriptor, event_mask in poll_result:
                queue = self._read_queues.get(file_descriptor, None)
                if queue is not None:
                    if event_mask & readable_events:
                        data = os.read(file_descriptor, 1024 * 32)
                        loop.call_soon_threadsafe(queue.put_nowait, data)

                    if event_mask & writeable_events:
                        write_queue = self._write_queues.get(file_descriptor, None)
                        if write_queue:
                            write = write_queue[0]
                            bytes_written = os.write(
                                file_descriptor, write.data[write.position :]
                            )
                            if bytes_written == len(write.data):
                                write_queue.popleft()
                                loop.call_soon_threadsafe(write.done_event.set)
                            else:
                                write.position += bytes_written

                    if event_mask & error_events:
                        loop.call_soon_threadsafe(queue.put_nowait, None)
                        self._read_queues.pop(file_descriptor, None)

    def exit(self) -> None:
        """Exit and block until finished."""
        for queue in self._read_queues.values():
            queue.put_nowait(None)
        self._exit_event.set()
        self.join()
        self._read_queues.clear()
        self._write_queues.clear()


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

    async def open(self, argv=None) -> None:
        pid, master_fd = pty.fork()
        self.pid = pid
        self.master_fd = master_fd

        if pid == pty.CHILD:
            if argv is None:
                argv = [self.command]
            try:
                os.execlp(argv[0], *argv)  ## Exits the app
            except Exception:
                os._exit(0)

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
            self._set_terminal_size(80, 24)

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
        if self._task is not None:
            await self._task
