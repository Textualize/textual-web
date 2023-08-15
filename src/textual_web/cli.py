import asyncio
import click
from pathlib import Path
import logging
import os
from rich.panel import Panel
import sys

from . import constants
from . import identity
from .environment import ENVIRONMENTS
from .ganglion_client import GanglionClient

from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text
import uvloop

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
@click.option("--config", help="Location of config file")
@click.option(
    "-e",
    "--environment",
    help="Environment (prod, dev, or local)",
    type=click.Choice(list(ENVIRONMENTS)),
    default=constants.ENVIRONMENT,
)
@click.option("-a", "--api-key", help="API key", default=constants.API_KEY)
@click.option(
    "-t", "--terminal", is_flag=True, help="Publish a remote terminal on a random URL"
)
def app(
    config: str | None,
    environment: str,
    terminal: bool,
    api_key: str,
) -> None:
    error_console = Console(stderr=True)
    from .config import load_config, default_config
    from .environment import get_environment

    _environment = get_environment(environment)

    print_disclaimer()
    log.info(f"environment={_environment!r}")

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

    ganglion_client = GanglionClient(
        config or "./", _config, _environment, api_key=api_key or None
    )

    if terminal:
        ganglion_client.add_terminal(
            "Terminal", os.environ.get("SHELL", "bin/sh"), identity.generate().lower()
        )

    if sys.version_info >= (3, 11):
        with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
            runner.run(ganglion_client.run())
    else:
        uvloop.install()
        asyncio.run(ganglion_client.run())
