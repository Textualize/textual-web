from __future__ import annotations

from typing import AsyncGenerator
from asyncio import Event, TimeoutError, wait_for
from random import random
import logging

log = logging.getLogger("textual-web")


class Retry:
    """Manage exponential backoff."""

    def __init__(
        self,
        done_event: Event | None = None,
        min_wait: float = 2.0,
        max_wait: float = 16.0,
    ) -> None:
        """
        Args:
            done_event: An event to exit the retry loop.
            min_wait: Minimum delay in seconds.
            max_wait: Maximum delay in seconds.
        """
        self.min_wait = min_wait
        self.max_wait = max_wait
        self._done_event = Event() if done_event is None else done_event
        self.retry_count = 0

    def success(self) -> None:
        """Call when connection was successful."""
        self.retry_count = 0

    def done(self) -> None:
        """Exit retry loop."""
        self._done_event.set()

    async def __aiter__(self) -> AsyncGenerator[int, object]:
        """Async iterator to manage timeouts."""
        while not self._done_event.is_set():
            self.retry_count = self.retry_count + 1
            yield self.retry_count

            retry_squared = self.retry_count**2
            sleep_for = random() * max(self.min_wait, min(self.max_wait, retry_squared))

            log.debug("Retrying after %dms", int(sleep_for * 1000.0))

            try:
                await wait_for(self._done_event.wait(), sleep_for)
            except TimeoutError:
                pass
