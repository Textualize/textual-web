"""
This file is auto-generated from packets.yml and packets.py.template

Time: Thu Jul 27 15:47:42 2023
Version: 1

To regenerate run `make packets.py` (in src directory)

**Do not hand edit.**


"""
from __future__ import annotations

from enum import IntEnum
from operator import attrgetter
from typing import ClassVar, Type

import rich.repr

MAX_STRING = 20


def abbreviate_repr(input: object) -> str:
    """Abbreviate any long strings."""
    if isinstance(input, (bytes, str)) and len(input) > MAX_STRING:
        cropped = len(input) - MAX_STRING
        return f"{input[:MAX_STRING]!r}+{cropped}"
    return repr(input)


class PacketType(IntEnum):
    """Enumeration of packet types."""

    # A null packet (never sent).
    NULL = 0
    # Request packet data to be returned via a Pong.
    PING = 1  # See Ping()

    # Response to a Ping packet. The data from Ping should be sent back in the Pong.
    PONG = 2  # See Pong()

    # A message to be written to debug logs. This is a debugging aid, and will be disabled in production.
    LOG = 3  # See Log()

    # Info message to be written in to logs. Unlike Log, these messages will be used in production.
    INFO = 4  # See Info()

    # Declare the apps exposed.
    DECLARE_APPS = 5  # See DeclareApps()

    # Notification sent by a client when an app session was opened
    SESSION_OPEN = 6  # See SessionOpen()

    # Close an existing app session.
    SESSION_CLOSE = 7  # See SessionClose()

    # Data for a session.
    SESSION_DATA = 8  # See SessionData()

    # Session ping
    ROUTE_PING = 9  # See RoutePing()

    # Session pong
    ROUTE_PONG = 10  # See RoutePong()

    # Notify the client that the terminal has change dimensions.
    NOTIFY_TERMINAL_SIZE = 11  # See NotifyTerminalSize()


class Packet(tuple):
    """Base class for a packet.

    Should never be sent. Use one of the derived classes.

    """

    sender: ClassVar[str] = "both"
    handler_name: ClassVar[str] = ""
    type: ClassVar[PacketType] = PacketType.NULL

    _attributes: ClassVar[list[tuple[str, Type]]] = []
    _attribute_count = 0
    _get_handler = attrgetter("foo")


# PacketType.PING (1)
class Ping(Packet):
    """Request packet data to be returned via a Pong.

    Args:
        data (bytes): Opaque data.

    """

    sender: ClassVar[str] = "both"
    """Permitted sender, should be "client", "server", or "both"."""
    handler_name: ClassVar[str] = "on_ping"
    """Name of the method used to handle this packet."""
    type: ClassVar[PacketType] = PacketType.PING
    """The packet type enumeration."""

    _attributes: ClassVar[list[tuple[str, Type]]] = [
        ("data", bytes),
    ]
    _attribute_count = 1
    _get_handler = attrgetter("on_ping")

    def __new__(cls, data: bytes) -> "Ping":
        return tuple.__new__(cls, (PacketType.PING, data))

    @classmethod
    def build(cls, data: bytes) -> "Ping":
        """Build and validate a packet from its attributes."""
        if not isinstance(data, bytes):
            raise TypeError(
                f'packets.Ping Type of "data" incorrect; expected bytes, found {type(data)}'
            )
        return tuple.__new__(cls, (PacketType.PING, data))

    def __repr__(self) -> str:
        _type, data = self
        return f"Ping({abbreviate_repr(data)})"

    def __rich_repr__(self) -> rich.repr.Result:
        yield "data", self.data

    @property
    def data(self) -> bytes:
        """Opaque data."""
        return self[1]


# PacketType.PONG (2)
class Pong(Packet):
    """Response to a Ping packet. The data from Ping should be sent back in the Pong.

    Args:
        data (bytes): Data received from PING

    """

    sender: ClassVar[str] = "both"
    """Permitted sender, should be "client", "server", or "both"."""
    handler_name: ClassVar[str] = "on_pong"
    """Name of the method used to handle this packet."""
    type: ClassVar[PacketType] = PacketType.PONG
    """The packet type enumeration."""

    _attributes: ClassVar[list[tuple[str, Type]]] = [
        ("data", bytes),
    ]
    _attribute_count = 1
    _get_handler = attrgetter("on_pong")

    def __new__(cls, data: bytes) -> "Pong":
        return tuple.__new__(cls, (PacketType.PONG, data))

    @classmethod
    def build(cls, data: bytes) -> "Pong":
        """Build and validate a packet from its attributes."""
        if not isinstance(data, bytes):
            raise TypeError(
                f'packets.Pong Type of "data" incorrect; expected bytes, found {type(data)}'
            )
        return tuple.__new__(cls, (PacketType.PONG, data))

    def __repr__(self) -> str:
        _type, data = self
        return f"Pong({abbreviate_repr(data)})"

    def __rich_repr__(self) -> rich.repr.Result:
        yield "data", self.data

    @property
    def data(self) -> bytes:
        """Data received from PING"""
        return self[1]


# PacketType.LOG (3)
class Log(Packet):
    """A message to be written to debug logs. This is a debugging aid, and will be disabled in production.

    Args:
        message (str): Message to log.

    """

    sender: ClassVar[str] = "both"
    """Permitted sender, should be "client", "server", or "both"."""
    handler_name: ClassVar[str] = "on_log"
    """Name of the method used to handle this packet."""
    type: ClassVar[PacketType] = PacketType.LOG
    """The packet type enumeration."""

    _attributes: ClassVar[list[tuple[str, Type]]] = [
        ("message", str),
    ]
    _attribute_count = 1
    _get_handler = attrgetter("on_log")

    def __new__(cls, message: str) -> "Log":
        return tuple.__new__(cls, (PacketType.LOG, message))

    @classmethod
    def build(cls, message: str) -> "Log":
        """Build and validate a packet from its attributes."""
        if not isinstance(message, str):
            raise TypeError(
                f'packets.Log Type of "message" incorrect; expected str, found {type(message)}'
            )
        return tuple.__new__(cls, (PacketType.LOG, message))

    def __repr__(self) -> str:
        _type, message = self
        return f"Log({abbreviate_repr(message)})"

    def __rich_repr__(self) -> rich.repr.Result:
        yield "message", self.message

    @property
    def message(self) -> str:
        """Message to log."""
        return self[1]


# PacketType.INFO (4)
class Info(Packet):
    """Info message to be written in to logs. Unlike Log, these messages will be used in production.

    Args:
        message (str): Info message

    """

    sender: ClassVar[str] = "server"
    """Permitted sender, should be "client", "server", or "both"."""
    handler_name: ClassVar[str] = "on_info"
    """Name of the method used to handle this packet."""
    type: ClassVar[PacketType] = PacketType.INFO
    """The packet type enumeration."""

    _attributes: ClassVar[list[tuple[str, Type]]] = [
        ("message", str),
    ]
    _attribute_count = 1
    _get_handler = attrgetter("on_info")

    def __new__(cls, message: str) -> "Info":
        return tuple.__new__(cls, (PacketType.INFO, message))

    @classmethod
    def build(cls, message: str) -> "Info":
        """Build and validate a packet from its attributes."""
        if not isinstance(message, str):
            raise TypeError(
                f'packets.Info Type of "message" incorrect; expected str, found {type(message)}'
            )
        return tuple.__new__(cls, (PacketType.INFO, message))

    def __repr__(self) -> str:
        _type, message = self
        return f"Info({abbreviate_repr(message)})"

    def __rich_repr__(self) -> rich.repr.Result:
        yield "message", self.message

    @property
    def message(self) -> str:
        """Info message"""
        return self[1]


# PacketType.DECLARE_APPS (5)
class DeclareApps(Packet):
    """Declare the apps exposed.

    Args:
        apps (list): Apps served by this client.

    """

    sender: ClassVar[str] = "client"
    """Permitted sender, should be "client", "server", or "both"."""
    handler_name: ClassVar[str] = "on_declare_apps"
    """Name of the method used to handle this packet."""
    type: ClassVar[PacketType] = PacketType.DECLARE_APPS
    """The packet type enumeration."""

    _attributes: ClassVar[list[tuple[str, Type]]] = [
        ("apps", list),
    ]
    _attribute_count = 1
    _get_handler = attrgetter("on_declare_apps")

    def __new__(cls, apps: list) -> "DeclareApps":
        return tuple.__new__(cls, (PacketType.DECLARE_APPS, apps))

    @classmethod
    def build(cls, apps: list) -> "DeclareApps":
        """Build and validate a packet from its attributes."""
        if not isinstance(apps, list):
            raise TypeError(
                f'packets.DeclareApps Type of "apps" incorrect; expected list, found {type(apps)}'
            )
        return tuple.__new__(cls, (PacketType.DECLARE_APPS, apps))

    def __repr__(self) -> str:
        _type, apps = self
        return f"DeclareApps({abbreviate_repr(apps)})"

    def __rich_repr__(self) -> rich.repr.Result:
        yield "apps", self.apps

    @property
    def apps(self) -> list:
        """Apps served by this client."""
        return self[1]


# PacketType.SESSION_OPEN (6)
class SessionOpen(Packet):
    """Notification sent by a client when an app session was opened

    Args:
        session_id (str): Session ID
        app_id (str): Application identity.
        application_slug (str): Application slug.
        route_key (str): Route key

    """

    sender: ClassVar[str] = "server"
    """Permitted sender, should be "client", "server", or "both"."""
    handler_name: ClassVar[str] = "on_session_open"
    """Name of the method used to handle this packet."""
    type: ClassVar[PacketType] = PacketType.SESSION_OPEN
    """The packet type enumeration."""

    _attributes: ClassVar[list[tuple[str, Type]]] = [
        ("session_id", str),
        ("app_id", str),
        ("application_slug", str),
        ("route_key", str),
    ]
    _attribute_count = 4
    _get_handler = attrgetter("on_session_open")

    def __new__(
        cls, session_id: str, app_id: str, application_slug: str, route_key: str
    ) -> "SessionOpen":
        return tuple.__new__(
            cls,
            (PacketType.SESSION_OPEN, session_id, app_id, application_slug, route_key),
        )

    @classmethod
    def build(
        cls, session_id: str, app_id: str, application_slug: str, route_key: str
    ) -> "SessionOpen":
        """Build and validate a packet from its attributes."""
        if not isinstance(session_id, str):
            raise TypeError(
                f'packets.SessionOpen Type of "session_id" incorrect; expected str, found {type(session_id)}'
            )
        if not isinstance(app_id, str):
            raise TypeError(
                f'packets.SessionOpen Type of "app_id" incorrect; expected str, found {type(app_id)}'
            )
        if not isinstance(application_slug, str):
            raise TypeError(
                f'packets.SessionOpen Type of "application_slug" incorrect; expected str, found {type(application_slug)}'
            )
        if not isinstance(route_key, str):
            raise TypeError(
                f'packets.SessionOpen Type of "route_key" incorrect; expected str, found {type(route_key)}'
            )
        return tuple.__new__(
            cls,
            (PacketType.SESSION_OPEN, session_id, app_id, application_slug, route_key),
        )

    def __repr__(self) -> str:
        _type, session_id, app_id, application_slug, route_key = self
        return f"SessionOpen({abbreviate_repr(session_id)}, {abbreviate_repr(app_id)}, {abbreviate_repr(application_slug)}, {abbreviate_repr(route_key)})"

    def __rich_repr__(self) -> rich.repr.Result:
        yield "session_id", self.session_id
        yield "app_id", self.app_id
        yield "application_slug", self.application_slug
        yield "route_key", self.route_key

    @property
    def session_id(self) -> str:
        """Session ID"""
        return self[1]

    @property
    def app_id(self) -> str:
        """Application identity."""
        return self[2]

    @property
    def application_slug(self) -> str:
        """Application slug."""
        return self[3]

    @property
    def route_key(self) -> str:
        """Route key"""
        return self[4]


# PacketType.SESSION_CLOSE (7)
class SessionClose(Packet):
    """Close an existing app session.

    Args:
        session_id (str): Session identity
        route_key (str): Route key

    """

    sender: ClassVar[str] = "server"
    """Permitted sender, should be "client", "server", or "both"."""
    handler_name: ClassVar[str] = "on_session_close"
    """Name of the method used to handle this packet."""
    type: ClassVar[PacketType] = PacketType.SESSION_CLOSE
    """The packet type enumeration."""

    _attributes: ClassVar[list[tuple[str, Type]]] = [
        ("session_id", str),
        ("route_key", str),
    ]
    _attribute_count = 2
    _get_handler = attrgetter("on_session_close")

    def __new__(cls, session_id: str, route_key: str) -> "SessionClose":
        return tuple.__new__(cls, (PacketType.SESSION_CLOSE, session_id, route_key))

    @classmethod
    def build(cls, session_id: str, route_key: str) -> "SessionClose":
        """Build and validate a packet from its attributes."""
        if not isinstance(session_id, str):
            raise TypeError(
                f'packets.SessionClose Type of "session_id" incorrect; expected str, found {type(session_id)}'
            )
        if not isinstance(route_key, str):
            raise TypeError(
                f'packets.SessionClose Type of "route_key" incorrect; expected str, found {type(route_key)}'
            )
        return tuple.__new__(cls, (PacketType.SESSION_CLOSE, session_id, route_key))

    def __repr__(self) -> str:
        _type, session_id, route_key = self
        return (
            f"SessionClose({abbreviate_repr(session_id)}, {abbreviate_repr(route_key)})"
        )

    def __rich_repr__(self) -> rich.repr.Result:
        yield "session_id", self.session_id
        yield "route_key", self.route_key

    @property
    def session_id(self) -> str:
        """Session identity"""
        return self[1]

    @property
    def route_key(self) -> str:
        """Route key"""
        return self[2]


# PacketType.SESSION_DATA (8)
class SessionData(Packet):
    """Data for a session.

    Args:
        route_key (str): Route index.
        data (bytes): Data for a remote app

    """

    sender: ClassVar[str] = "both"
    """Permitted sender, should be "client", "server", or "both"."""
    handler_name: ClassVar[str] = "on_session_data"
    """Name of the method used to handle this packet."""
    type: ClassVar[PacketType] = PacketType.SESSION_DATA
    """The packet type enumeration."""

    _attributes: ClassVar[list[tuple[str, Type]]] = [
        ("route_key", str),
        ("data", bytes),
    ]
    _attribute_count = 2
    _get_handler = attrgetter("on_session_data")

    def __new__(cls, route_key: str, data: bytes) -> "SessionData":
        return tuple.__new__(cls, (PacketType.SESSION_DATA, route_key, data))

    @classmethod
    def build(cls, route_key: str, data: bytes) -> "SessionData":
        """Build and validate a packet from its attributes."""
        if not isinstance(route_key, str):
            raise TypeError(
                f'packets.SessionData Type of "route_key" incorrect; expected str, found {type(route_key)}'
            )
        if not isinstance(data, bytes):
            raise TypeError(
                f'packets.SessionData Type of "data" incorrect; expected bytes, found {type(data)}'
            )
        return tuple.__new__(cls, (PacketType.SESSION_DATA, route_key, data))

    def __repr__(self) -> str:
        _type, route_key, data = self
        return f"SessionData({abbreviate_repr(route_key)}, {abbreviate_repr(data)})"

    def __rich_repr__(self) -> rich.repr.Result:
        yield "route_key", self.route_key
        yield "data", self.data

    @property
    def route_key(self) -> str:
        """Route index."""
        return self[1]

    @property
    def data(self) -> bytes:
        """Data for a remote app"""
        return self[2]


# PacketType.ROUTE_PING (9)
class RoutePing(Packet):
    """Session ping

    Args:
        route_key (str): Route index.
        data (str): Opaque data.

    """

    sender: ClassVar[str] = "server"
    """Permitted sender, should be "client", "server", or "both"."""
    handler_name: ClassVar[str] = "on_route_ping"
    """Name of the method used to handle this packet."""
    type: ClassVar[PacketType] = PacketType.ROUTE_PING
    """The packet type enumeration."""

    _attributes: ClassVar[list[tuple[str, Type]]] = [
        ("route_key", str),
        ("data", str),
    ]
    _attribute_count = 2
    _get_handler = attrgetter("on_route_ping")

    def __new__(cls, route_key: str, data: str) -> "RoutePing":
        return tuple.__new__(cls, (PacketType.ROUTE_PING, route_key, data))

    @classmethod
    def build(cls, route_key: str, data: str) -> "RoutePing":
        """Build and validate a packet from its attributes."""
        if not isinstance(route_key, str):
            raise TypeError(
                f'packets.RoutePing Type of "route_key" incorrect; expected str, found {type(route_key)}'
            )
        if not isinstance(data, str):
            raise TypeError(
                f'packets.RoutePing Type of "data" incorrect; expected str, found {type(data)}'
            )
        return tuple.__new__(cls, (PacketType.ROUTE_PING, route_key, data))

    def __repr__(self) -> str:
        _type, route_key, data = self
        return f"RoutePing({abbreviate_repr(route_key)}, {abbreviate_repr(data)})"

    def __rich_repr__(self) -> rich.repr.Result:
        yield "route_key", self.route_key
        yield "data", self.data

    @property
    def route_key(self) -> str:
        """Route index."""
        return self[1]

    @property
    def data(self) -> str:
        """Opaque data."""
        return self[2]


# PacketType.ROUTE_PONG (10)
class RoutePong(Packet):
    """Session pong

    Args:
        route_key (str): Route index.
        data (str): Opaque data.

    """

    sender: ClassVar[str] = "both"
    """Permitted sender, should be "client", "server", or "both"."""
    handler_name: ClassVar[str] = "on_route_pong"
    """Name of the method used to handle this packet."""
    type: ClassVar[PacketType] = PacketType.ROUTE_PONG
    """The packet type enumeration."""

    _attributes: ClassVar[list[tuple[str, Type]]] = [
        ("route_key", str),
        ("data", str),
    ]
    _attribute_count = 2
    _get_handler = attrgetter("on_route_pong")

    def __new__(cls, route_key: str, data: str) -> "RoutePong":
        return tuple.__new__(cls, (PacketType.ROUTE_PONG, route_key, data))

    @classmethod
    def build(cls, route_key: str, data: str) -> "RoutePong":
        """Build and validate a packet from its attributes."""
        if not isinstance(route_key, str):
            raise TypeError(
                f'packets.RoutePong Type of "route_key" incorrect; expected str, found {type(route_key)}'
            )
        if not isinstance(data, str):
            raise TypeError(
                f'packets.RoutePong Type of "data" incorrect; expected str, found {type(data)}'
            )
        return tuple.__new__(cls, (PacketType.ROUTE_PONG, route_key, data))

    def __repr__(self) -> str:
        _type, route_key, data = self
        return f"RoutePong({abbreviate_repr(route_key)}, {abbreviate_repr(data)})"

    def __rich_repr__(self) -> rich.repr.Result:
        yield "route_key", self.route_key
        yield "data", self.data

    @property
    def route_key(self) -> str:
        """Route index."""
        return self[1]

    @property
    def data(self) -> str:
        """Opaque data."""
        return self[2]


# PacketType.NOTIFY_TERMINAL_SIZE (11)
class NotifyTerminalSize(Packet):
    """Notify the client that the terminal has change dimensions.

    Args:
        session_id (str): Session identity.
        width (int): Width of the terminal.
        height (int): Height of the terminal.

    """

    sender: ClassVar[str] = "server"
    """Permitted sender, should be "client", "server", or "both"."""
    handler_name: ClassVar[str] = "on_notify_terminal_size"
    """Name of the method used to handle this packet."""
    type: ClassVar[PacketType] = PacketType.NOTIFY_TERMINAL_SIZE
    """The packet type enumeration."""

    _attributes: ClassVar[list[tuple[str, Type]]] = [
        ("session_id", str),
        ("width", int),
        ("height", int),
    ]
    _attribute_count = 3
    _get_handler = attrgetter("on_notify_terminal_size")

    def __new__(cls, session_id: str, width: int, height: int) -> "NotifyTerminalSize":
        return tuple.__new__(
            cls, (PacketType.NOTIFY_TERMINAL_SIZE, session_id, width, height)
        )

    @classmethod
    def build(cls, session_id: str, width: int, height: int) -> "NotifyTerminalSize":
        """Build and validate a packet from its attributes."""
        if not isinstance(session_id, str):
            raise TypeError(
                f'packets.NotifyTerminalSize Type of "session_id" incorrect; expected str, found {type(session_id)}'
            )
        if not isinstance(width, int):
            raise TypeError(
                f'packets.NotifyTerminalSize Type of "width" incorrect; expected int, found {type(width)}'
            )
        if not isinstance(height, int):
            raise TypeError(
                f'packets.NotifyTerminalSize Type of "height" incorrect; expected int, found {type(height)}'
            )
        return tuple.__new__(
            cls, (PacketType.NOTIFY_TERMINAL_SIZE, session_id, width, height)
        )

    def __repr__(self) -> str:
        _type, session_id, width, height = self
        return f"NotifyTerminalSize({abbreviate_repr(session_id)}, {abbreviate_repr(width)}, {abbreviate_repr(height)})"

    def __rich_repr__(self) -> rich.repr.Result:
        yield "session_id", self.session_id
        yield "width", self.width
        yield "height", self.height

    @property
    def session_id(self) -> str:
        """Session identity."""
        return self[1]

    @property
    def width(self) -> int:
        """Width of the terminal."""
        return self[2]

    @property
    def height(self) -> int:
        """Height of the terminal."""
        return self[3]


# A mapping of the packet id on to the packet class
PACKET_MAP: dict[int, type[Packet]] = {
    1: Ping,
    2: Pong,
    3: Log,
    4: Info,
    5: DeclareApps,
    6: SessionOpen,
    7: SessionClose,
    8: SessionData,
    9: RoutePing,
    10: RoutePong,
    11: NotifyTerminalSize,
}

# A mapping of the packet name on to the packet class
PACKET_NAME_MAP: dict[str, type[Packet]] = {
    "ping": Ping,
    "pong": Pong,
    "log": Log,
    "info": Info,
    "declareapps": DeclareApps,
    "sessionopen": SessionOpen,
    "sessionclose": SessionClose,
    "sessiondata": SessionData,
    "routeping": RoutePing,
    "routepong": RoutePong,
    "notifyterminalsize": NotifyTerminalSize,
}


class Handlers:
    """Base class for handlers."""

    async def dispatch_packet(self, packet: Packet) -> None:
        """Dispatch a packet to the appropriate handler.

        Args:
            packet (Packet): A packet object.

        """

        await packet._get_handler(self)(packet)

    async def on_ping(self, packet: Ping) -> None:
        """Request packet data to be returned via a Pong."""
        await self.on_default(packet)

    async def on_pong(self, packet: Pong) -> None:
        """Response to a Ping packet. The data from Ping should be sent back in the Pong."""
        await self.on_default(packet)

    async def on_log(self, packet: Log) -> None:
        """A message to be written to debug logs. This is a debugging aid, and will be disabled in production."""
        await self.on_default(packet)

    async def on_info(self, packet: Info) -> None:
        """Info message to be written in to logs. Unlike Log, these messages will be used in production."""
        await self.on_default(packet)

    async def on_declare_apps(self, packet: DeclareApps) -> None:
        """Declare the apps exposed."""
        await self.on_default(packet)

    async def on_session_open(self, packet: SessionOpen) -> None:
        """Notification sent by a client when an app session was opened"""
        await self.on_default(packet)

    async def on_session_close(self, packet: SessionClose) -> None:
        """Close an existing app session."""
        await self.on_default(packet)

    async def on_session_data(self, packet: SessionData) -> None:
        """Data for a session."""
        await self.on_default(packet)

    async def on_route_ping(self, packet: RoutePing) -> None:
        """Session ping"""
        await self.on_default(packet)

    async def on_route_pong(self, packet: RoutePong) -> None:
        """Session pong"""
        await self.on_default(packet)

    async def on_notify_terminal_size(self, packet: NotifyTerminalSize) -> None:
        """Notify the client that the terminal has change dimensions."""
        await self.on_default(packet)

    async def on_default(self, packet: Packet) -> None:
        """Called when a packet is not handled."""


if __name__ == "__main__":
    print("packets.py imported successfully")
