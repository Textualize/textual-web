from __future__ import annotations

import asyncio
import logging
from pathlib import Path
import platform

from . import config
from .identity import generate

from .app_session import AppSession
from .session import Session

from .poller import Poller
from .types import SessionID, RouteKey
from ._two_way_dict import TwoWayDict

WINDOWS = platform.system() == "Windows"


log = logging.getLogger("textual-web")


if not WINDOWS:
    from .terminal_session import TerminalSession


class SessionManager:
    """Manage sessions (Textual apps or terminals)."""

    def __init__(self, poller: Poller, path: Path, apps: list[config.App]) -> None:
        self.poller = poller
        self.path = path
        self.apps = apps
        self.apps_by_slug = {app.slug: app for app in apps}
        self.sessions: dict[SessionID, Session] = {}
        self.routes: TwoWayDict[RouteKey, SessionID] = TwoWayDict()

    def add_app(
        self, name: str, command: str, slug: str, terminal: bool = False
    ) -> None:
        """Add a new app

        Args:
            name: Name of the app.
            command: Command to run the app.
            slug: Slug used in URL, or blank to auto-generate on server.
        """
        slug = slug or generate().lower()
        new_app = config.App(
            name=name, slug=slug, path="./", command=command, terminal=terminal
        )
        self.apps.append(new_app)
        self.apps_by_slug[slug] = new_app

    def on_session_end(self, session_id: SessionID) -> None:
        """Called by sessions."""
        self.sessions.pop(session_id)
        route_key = self.routes.get_key(session_id)
        if route_key is not None:
            del self.routes[route_key]

    async def close_all(self, timeout: float = 3.0) -> None:
        """Close app sessions.

        Args:
            timeout: Time (in seconds) to wait before giving up.

        """
        sessions = list(self.sessions.values())

        if not sessions:
            return
        log.info("Closing %s session(s)", len(sessions))

        async def do_close() -> int:
            """Close all sessions, return number unclosed after timeout

            Returns:
                Number of sessions not yet closed.
            """

            async def close_wait(session: Session) -> None:
                await session.close()
                await session.wait()

            _done, remaining = await asyncio.wait(
                [asyncio.create_task(close_wait(session)) for session in sessions],
                timeout=timeout,
            )
            return len(remaining)

        remaining = await do_close()
        if remaining:
            log.warning("%s session(s) didn't close after %s seconds", timeout)

    async def new_session(
        self,
        slug: str,
        session_id: SessionID,
        route_key: RouteKey,
        devtools: bool = False,
        size: tuple[int, int] = (80, 24),
    ) -> Session | None:
        """Create a new seession.

        Args:
            slug: Slug for app.
            session_id: Session identity.
            route_key: Route key.
            devtools: Enable devtools in Textual apps

        Returns:
            New session, or `None` if no app / terminal configured.
        """
        app = self.apps_by_slug.get(slug)
        if app is None:
            return None

        session_process: Session
        if app.terminal:
            if WINDOWS:
                log.warn(
                    "Sorry, textual-web does not currently support terminals on Windows"
                )
                return None
            else:
                session_process = TerminalSession(
                    self.poller,
                    session_id,
                    app.command,
                )
        else:
            session_process = AppSession(
                self.path,
                app.command,
                session_id,
                devtools=devtools,
            )
        self.sessions[session_id] = session_process
        self.routes[route_key] = session_id

        await session_process.open(*size)

        return session_process

    async def close_session(self, session_id: SessionID) -> None:
        """Close a session.

        Args:
            session_id: Session identity.
        """
        session_process = self.sessions.get(session_id, None)
        if session_process is None:
            return
        await session_process.close()

    def get_session(self, session_id: SessionID) -> Session | None:
        """Get a session from a session ID.

        Args:
            session_id: Session identity.

        Returns:
            A session or `None` if it doesn't exist.
        """
        return self.sessions.get(session_id)

    def get_session_by_route_key(self, route_key: RouteKey) -> Session | None:
        """Get a session from a route key.

        Args:
            route_key: A route key.

        Returns:
            A session or `None` if it doesn't exist.

        """
        session_id = self.routes.get(route_key)
        if session_id is not None:
            return self.sessions.get(session_id)
        else:
            return None
