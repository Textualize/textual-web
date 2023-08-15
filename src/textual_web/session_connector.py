class SessionConnector:
    async def on_data(self, data: bytes) -> None:
        """Data received from the process."""
        await self.send(packets.SessionData(route_key, data))

    async def on_meta(self, meta: dict) -> None:
        pass

    async def on_close(self) -> None:
        await self.send(packets.SessionClose(packet.session_id, route_key))
