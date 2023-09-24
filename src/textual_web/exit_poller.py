from __future__ import annotations

import asyncio
import logging
from time import monotonic
from typing import TYPE_CHECKING

EXIT_POLL_RATE = 5

log = logging.getLogger("textual-web")

if TYPE_CHECKING:
    from .ganglion_client import GanglionClient


class ExitPoller:
    """Monitors the client for an idle state, and exits."""

    def __init__(self, client: GanglionClient, idle_wait: int) -> None:
        self.client = client
        self.idle_wait = idle_wait
        self._task: asyncio.Task | None = None
        self._idle_start_time: float | None = None

    def start(self) -> None:
        """Start polling."""
        self._task = asyncio.create_task(self.run())

    def stop(self) -> None:
        """Stop polling"""
        if self._task is not None:
            self._task.cancel()

    async def run(self) -> None:
        """Run the poller."""
        if not self.idle_wait:
            return
        try:
            while True:
                await asyncio.sleep(EXIT_POLL_RATE)
                is_idle = not self.client.session_manager.sessions
                if is_idle:
                    if self._idle_start_time is not None:
                        if monotonic() - self._idle_start_time > self.idle_wait:
                            log.info("Exiting due to --exit-on-idle")
                            self.client.force_exit()
                    else:
                        self._idle_start_time = monotonic()
                else:
                    self._idle_start_time = None

        except asyncio.CancelledError:
            pass
