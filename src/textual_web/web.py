"""
An optional web interface to control textual-web

Note: Currently just a stub.

"""

import logging

import asyncio
from aiohttp import web


log = logging.getLogger("textual-web")


async def run_web_interface(connected_event: asyncio.Event) -> web.Application:
    """Run the web interface."""

    async def health_check(request) -> web.Response:
        await asyncio.wait_for(connected_event.wait(), 5.0)
        return web.Response(text="Hello, world")

    app = web.Application()
    app.add_routes([web.get("/health-check/", health_check)])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    log.info("Web interface started on port 8080")
    return app
