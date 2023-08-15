from __future__ import annotations

from typing_extensions import Protocol
from .types import Meta, RouteKey


class SessionHandler:
    def __init__(self, route_key: RouteKey) -> None:
        self.route_key = route_key

    async def on_data(self, data: bytes) -> None:
        pass

    async def on_meta(self, meta: Meta) -> None:
        pass

    async def on_close(self) -> None:
        pass
