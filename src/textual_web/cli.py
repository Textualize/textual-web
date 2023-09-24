from __future__ import annotations

import asyncio
import click
from pathlib import Path
import logging
import os
import platform
from rich.panel import Panel
import sys

from . import constants
from . import identity
from .environment import ENVIRONMENTS
from .ganglion_client import GanglionClient

from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text

from importlib_metadata import version

WINDOWS = platform.system() == "Windows"

if constants.DEBUG:
    FORMAT = "%(message)s"
    logging.basicConfig(
        level="DEBUG",
        format=FORMAT,
        datefmt="[%X]",
        handlers=[RichHandler(show_path=False)],
    )
else:
    FORMAT = "%(message)s"
    logging.basicConfig(
        level="INFO",
        format=FORMAT,
        datefmt="[%X]",
        handlers=[RichHandler(show_path=False)],
    )

log = logging.getLogger("textual-web")


def print_disclaimer() -> None:
    """Print a disclaimer message."""
    from rich import print
    from rich import box

    panel = Panel.fit(
        Text.from_markup(
            "[b]textual-web is currently under active development, and not suitable for production use.[/b]\n\n"
            "For support, please join the [blue][link=https://discord.gg/Enf6Z3qhVr]Discord server[/link]",
        ),
        border_style="red",
        box=box.HEAVY,
        title="[b]Disclaimer",
        padding=(1, 2),
    )
    print(panel)


@click.command()
@click.version_option(version("textual-web"))
@click.option("-c", "--config", help="Location of TOML config file.", metavar="PATH")
@click.option(
    "-e",
    "--environment",
    help="Environment switch.",
    type=click.Choice(list(ENVIRONMENTS)),
    default=constants.ENVIRONMENT,
)
@click.option("-a", "--api-key", help="API key", default=constants.API_KEY)
@click.option(
    "-r",
    "--run",
    help="Command to run a Textual app.",
    multiple=True,
    metavar="COMMAND",
)
@click.option(
    "--dev", is_flag=True, help="Enable devtools in Textual apps.", default=False
)
@click.option(
    "-t", "--terminal", is_flag=True, help="Publish a remote terminal on a random URL."
)
@click.option(
    "-x",
    "--exit-on-idle",
    type=int,
    metavar="WAIT",
    default=0,
    help="Exit textual-web when no apps have been launched in WAIT seconds",
)
@click.option("-w", "--web-interface", is_flag=True, help="Enable web interface")
@click.option("-s", "--signup", is_flag=True, help="Create a textual-web account.")
@click.option("--welcome", is_flag=True, help="Launch an example app.")
@click.option("--merlin", is_flag=True, help="Launch Merlin game.")
def app(
    config: str | None,
    environment: str,
    run: list[str],
    dev: bool,
    terminal: bool,
    exit_on_idle: int,
    web_interface: bool,
    api_key: str,
    signup: bool,
    welcome: bool,
    merlin: bool,
) -> None:
    """Textual-web can server Textual apps and terminals."""

    # Args:
    #     config: Path to config.
    #     environment: environment switch.
    #     devtools: Enable devtools.
    #     terminal: Enable a terminal.
    #     api_key: API key.
    #     signup: Signup dialog.
    #     welcome: Welcome app.
    #     merlin: Merlin app.

    error_console = Console(stderr=True)
    from .config import load_config, default_config
    from .environment import get_environment

    _environment = get_environment(environment)

    if signup:
        from .apps.signup import SignUpApp

        SignUpApp.signup(_environment)
        return

    if welcome:
        from .apps.welcome import WelcomeApp

        WelcomeApp().run()
        return

    if merlin:
        from .apps.merlin import MerlinApp

        MerlinApp().run()
        return

    VERSION = version("textual-web")

    print_disclaimer()
    log.info(f"version='{VERSION}'")
    if constants.DEBUG:
        log.info(f"environment={_environment!r}")
    else:
        log.info(f"environment={_environment.name!r}")

    if constants.DEBUG:
        log.warning("DEBUG env var is set; logs may be verbose!")

    if config is not None:
        path = Path(config).absolute()
        log.info(f"loading config from {str(path)!r}")
        try:
            _config = load_config(path)
        except FileNotFoundError:
            log.critical("Config not found")
            return
        except Exception as error:
            error_console.print(f"Failed to load config from {str(path)!r}; {error!r}")
            return
    else:
        log.info("No --config specified, using defaults.")
        _config = default_config()

    if constants.DEBUG:
        from rich import print

        print(_config)

    if dev:
        log.info("Devtools enabled in Textual apps (run textual console)")

    ganglion_client = GanglionClient(
        config or "./",
        _config,
        _environment,
        api_key=api_key or None,
        devtools=dev,
        exit_on_idle=exit_on_idle,
        web_interface=web_interface,
    )

    for app_command in run:
        ganglion_client.add_app(app_command, app_command, "")

    if terminal:
        ganglion_client.add_terminal(
            "Terminal",
            os.environ.get("SHELL", "bin/sh"),
            "",
        )

    if not ganglion_client.app_count:
        ganglion_client.add_app("Welcome", "textual-web --welcome", "welcome")
        ganglion_client.add_app("Merlin Tribute", "textual-web --merlin", "merlin")

    if WINDOWS:
        asyncio.run(ganglion_client.run())
    else:
        try:
            import uvloop
        except ImportError:
            asyncio.run(ganglion_client.run())
        else:
            if sys.version_info >= (3, 11):
                with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
                    runner.run(ganglion_client.run())
            else:
                uvloop.install()
                asyncio.run(ganglion_client.run())


if __name__ == "__main__":
    app()
