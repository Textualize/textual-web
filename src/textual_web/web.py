"""
An optional web interface to control textual-web

Note: Currently just a stub.

"""

import logging

from aiohttp import web


log = logging.getLogger("textual-web")


async def run_web_interface() -> web.Application:
    """Run the web interface."""

    async def health_check(request) -> web.Response:
        return web.Response(text="Hello, world")

    app = web.Application()
    app.add_routes([web.get("/health-check/", health_check)])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    log.info("Web interface started on port 8080")
    return app
