from __future__ import annotations

import asyncio
import logging
import signal
from functools import partial
from pathlib import Path
import platform
from typing import TYPE_CHECKING, Union, cast

import aiohttp
import msgpack

from . import constants, packets
from .environment import Environment
from .packets import (
    PACKET_MAP,
    Handlers,
    NotifyTerminalSize,
    Packet,
    RoutePing,
    RoutePong,
    SessionClose,
    SessionData,
)
from .poller import Poller
from .retry import Retry
from .session import SessionConnector
from .session_manager import SessionManager
from .types import Meta, RouteKey, SessionID

if TYPE_CHECKING:
    from .config import Config

WINDOWS = platform.system() == "Windows"

log = logging.getLogger("textual-web")


PacketDataType = Union[int, bytes, str, None]


class PacketError(Exception):
    """A packet error."""


class _ClientConnector(SessionConnector):
    def __init__(
        self, client: GanglionClient, session_id: SessionID, route_key: RouteKey
    ) -> None:
        self.client = client
        self.session_id = session_id
        self.route_key = route_key

    async def on_data(self, data: bytes) -> None:
        """Data received from the process."""
        await self.client.send(packets.SessionData(self.route_key, data))

    async def on_meta(self, meta: Meta) -> None:
        pass

    async def on_close(self) -> None:
        await self.client.send(packets.SessionClose(self.session_id, self.route_key))
        self.client.session_manager.on_session_end(self.session_id)


class GanglionClient(Handlers):
    """Manages a connection to a ganglion server."""

    def __init__(
        self,
        config_path: str,
        config: Config,
        environment: Environment,
        api_key: str | None,
        devtools: bool = False,
    ) -> None:
        self.environment = environment
        self.websocket_url = environment.url

        path = Path(config_path).absolute().parent
        self.config = config
        self.api_key = api_key
        self._devtools = devtools
        self._websocket: aiohttp.ClientWebSocketResponse | None = None
        self._poller = Poller()
        self.session_manager = SessionManager(self._poller, path, config.apps)
        self.exit_event = asyncio.Event()
        self._task: asyncio.Task | None = None

    @property
    def app_count(self) -> int:
        """The number of configured apps."""
        return len(self.session_manager.apps)

    def add_app(self, name: str, command: str, slug: str = "") -> None:
        """Add a new app

        Args:
            name: Name of the app.
            command: Command to run the app.
            slug: Slug used in URL, or blank to auto-generate on server.
        """
        self.session_manager.add_app(name, command, slug=slug)

    def add_terminal(self, name: str, command: str, slug: str = "") -> None:
        """Add a new terminal.

        Args:
            name: Name of the app.
            command: Command to run the app.
            slug: Slug used in URL, or blank to auto-generate on server.
        """
        if WINDOWS:
            log.warning(
                "Sorry, textual-web does not currently support terminals on Windows"
            )
        else:
            self.session_manager.add_app(name, command, slug=slug, terminal=True)

    @classmethod
    def decode_envelope(
        cls, packet_envelope: tuple[PacketDataType, ...]
    ) -> Packet | None:
        """Decode a packet envelope.

        Packet envelopes are a list where the first value is an integer denoting the type.
        The type is used to look up the appropriate Packet class which is instantiated with
        the rest of the data.

        If the envelope contains *more* data than required, then that data is silently dropped.
        This is to provide an extension mechanism.

        Raises:
            PacketError: If the packet_envelope is empty.
            PacketError: If the packet type is not an int.

        Returns:
            One of the Packet classes defined in packets.py or None if the packet was of an unknown type.
        """
        if not packet_envelope:
            raise PacketError("Packet data is empty")

        packet_data: list[PacketDataType]
        packet_type, *packet_data = packet_envelope
        if not isinstance(packet_type, int):
            raise PacketError(f"Packet id expected int, found {packet_type!r}")
        packet_class = PACKET_MAP.get(packet_type, None)
        if packet_class is None:
            return None
        try:
            packet = packet_class.build(*packet_data[: len(packet_class._attributes)])
        except TypeError as error:
            raise PacketError(f"Packet failed to validate; {error}")
        return packet

    async def run(self) -> None:
        """Run the connection loop."""
        try:
            await self._run()
        finally:
            # Shut down the poller thread
            if not WINDOWS:
                try:
                    self._poller.exit()
                except Exception:
                    pass

    def on_keyboard_interrupt(self) -> None:
        """Signal handler to respond to keyboard interrupt."""
        print(
            "\r\033[F"
        )  # Move to start of line, to overwrite "^C" written by the shell (?)
        log.info("Exit requested")
        self.exit_event.set()
        if self._task is not None:
            self._task.cancel()

    async def _run(self) -> None:
        loop = asyncio.get_event_loop()
        if WINDOWS:

            def exit_handler(signal_handler, stack_frame) -> None:
                """Signal handler."""
                self.on_keyboard_interrupt()

            signal.signal(signal.SIGINT, exit_handler)
        else:
            loop.add_signal_handler(signal.SIGINT, self.on_keyboard_interrupt)
            self._poller.set_loop(loop)
            self._poller.start()

        self._task = asyncio.create_task(self.connect())
        await self._task

    async def connect(self) -> None:
        """Connect to the Ganglion server."""
        try:
            await self._connect()
        except asyncio.CancelledError:
            pass

    async def _connect(self) -> None:
        """Internal connect."""
        api_key = self.config.account.api_key or self.api_key or None
        if api_key:
            headers = {"GANGLIONAPIKEY": api_key}
        else:
            headers = {}

        retry = Retry()

        async for retry_count in retry:
            if self.exit_event.is_set():
                break
            try:
                if retry_count == 1:
                    log.info("connecting to Ganglion")
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(
                        self.websocket_url,
                        headers=headers,
                        heartbeat=15,  # Sends a regular ping
                        compress=12,  # Enables websocket compression
                    ) as websocket:
                        self._websocket = websocket
                        retry.success()
                        await self.post_connect()
                        try:
                            await self.run_websocket(websocket, retry)
                        finally:
                            self._websocket = None
                            log.info("Disconnected from Ganglion")
                if self.exit_event.is_set():
                    break
            except asyncio.CancelledError:
                raise
            except Exception as error:
                if retry_count == 1:
                    log.warning(
                        "Unable to connect to Ganglion server. Will reattempt connection soon."
                    )
                if constants.DEBUG:
                    log.error("Unable to connect; %s", error)

    async def run_websocket(
        self, websocket: aiohttp.ClientWebSocketResponse, retry: Retry
    ) -> None:
        """Run the websocket loop.

        Args:
            websocket: Websocket.
        """
        unpackb = partial(msgpack.unpackb, use_list=True, raw=False)
        BINARY = aiohttp.WSMsgType.BINARY

        async def run_messages() -> None:
            """Read, decode, and dispatch websocket messages."""
            async for message in websocket:
                if message.type == BINARY:
                    try:
                        envelope = unpackb(message.data)
                    except Exception:
                        log.error(f"Unable to decode {message.data!r}")
                    else:
                        packet = self.decode_envelope(envelope)
                        log.debug("<RECV> %r", packet)
                        if packet is not None:
                            try:
                                await self.dispatch_packet(packet)
                            except Exception:
                                log.exception("error processing %r", packet)

                elif message.type == aiohttp.WSMsgType.ERROR:
                    break

        try:
            await run_messages()
        except asyncio.CancelledError:
            retry.done()
            await self.session_manager.close_all()
            await websocket.close(message=b"Close requested")
            try:
                await run_messages()
            except asyncio.CancelledError:
                pass
        except ConnectionResetError:
            log.info("connection reset")
        except Exception as error:
            log.exception(str(error))

    async def post_connect(self) -> None:
        """Called immediately after connecting to server."""
        # Inform the server about our apps
        apps = [
            app.model_dump(include={"name", "slug", "color", "terminal"})
            for app in self.config.apps
        ]
        if WINDOWS:
            filter_apps = [app for app in apps if not app["terminal"]]
            if filter_apps != apps:
                log.warn(
                    "Sorry, textual-web does not currently support terminals on Windows"
                )
            apps = filter_apps

        await self.send(packets.DeclareApps(apps))

    async def send(self, packet: Packet) -> bool:
        """Send a packet.

        Args:
            packet: Packet to send.

        Returns:
            bool: `True` if the packet was sent, otherwise `False`.
        """
        if self._websocket is None:
            log.warning("Failed to send %r", packet)
            return False
        packet_bytes = msgpack.packb(packet, use_bin_type=True)
        try:
            await self._websocket.send_bytes(packet_bytes)
        except Exception as error:
            log.warning("Failed to send %r; %s", packet, error)
            return False
        else:
            log.debug("<SEND> %r", packet)
        return True

    async def on_ping(self, packet: packets.Ping) -> None:
        """Sent by the server."""
        # Reply to a Ping with an immediate Pong.
        await self.send(packets.Pong(packet.data))

    async def on_log(self, packet: packets.Log) -> None:
        """A log message sent by the server."""
        log.debug(f"<ganglion> {packet.message}")

    async def on_info(self, packet: packets.Info) -> None:
        """An info message (higher priority log) sent by the server."""
        log.info(f"<ganglion> {packet.message}")

    async def on_session_open(self, packet: packets.SessionOpen) -> None:
        route_key = packet.route_key
        session_process = await self.session_manager.new_session(
            packet.application_slug,
            SessionID(packet.session_id),
            RouteKey(packet.route_key),
            devtools=self._devtools,
            size=(packet.width, packet.height),
        )
        if session_process is None:
            log.debug("Failed to create session")
            return

        connector = _ClientConnector(
            self, cast(SessionID, packet.session_id), cast(RouteKey, route_key)
        )
        await session_process.start(connector)

    async def on_session_close(self, packet: SessionClose) -> None:
        session_id = SessionID(packet.session_id)
        session_process = self.session_manager.get_session(session_id)
        if session_process is not None:
            await self.session_manager.close_session(session_id)

    async def on_session_data(self, packet: SessionData) -> None:
        session_process = self.session_manager.get_session_by_route_key(
            RouteKey(packet.route_key)
        )
        if session_process is not None:
            await session_process.send_bytes(packet.data)

    async def on_notify_terminal_size(self, packet: NotifyTerminalSize) -> None:
        session_process = self.session_manager.get_session(SessionID(packet.session_id))
        if session_process is not None:
            await session_process.set_terminal_size(packet.width, packet.height)

    async def on_route_ping(self, packet: RoutePing) -> None:
        await self.send(RoutePong(packet.route_key, packet.data))
