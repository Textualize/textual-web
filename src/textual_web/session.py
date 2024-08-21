from __future__ import annotations

from abc import ABC, abstractmethod
import asyncio
from .types import Meta


class SessionConnector:
    """Connect a session with a client."""

    async def on_data(self, data: bytes) -> None:
        """Handle data from session.

        Args:
            data: Bytes to handle.
        """

    async def on_meta(self, meta: Meta) -> None:
        """Handle meta from session.

        Args:
            meta: Mapping of meta information.
        """

    async def on_binary_encoded_message(self, payload: bytes) -> None:
        """Handle binary encoded data from the process.

        Args:
            payload: Binary encoded data to handle.
        """

    async def on_close(self) -> None:
        """Handle session close."""


class Session(ABC):
    """Virtual base class for a session."""

    def __init__(self) -> None:
        self._connector = SessionConnector()

    @abstractmethod
    async def open(self, width: int = 80, height: int = 24) -> None:
        """Open the session."""
        ...

    @abstractmethod
    async def start(self, connector: SessionConnector) -> asyncio.Task:
        """Start the session.

        Returns:
            Running task.
        """
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close the session."""

    @abstractmethod
    async def wait(self) -> None:
        """Wait for session to end."""

    @abstractmethod
    async def set_terminal_size(self, width: int, height: int) -> None:
        """Set the terminal size.

        Args:
            width: New width.
            height: New height.
        """
        ...

    @abstractmethod
    async def send_bytes(self, data: bytes) -> bool:
        """Send bytes to the process.

        Args:
            data: Bytes to send.

        Returns:
            True on success, or False if the data was not sent.
        """
        ...

    @abstractmethod
    async def send_meta(self, data: Meta) -> bool:
        """Send meta to the process.

        Args:
            meta: Meta information.

        Returns:
            True on success, or False if the data was not sent.
        """
        ...
