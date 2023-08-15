from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Environment:
    """Data structure to describe the environment (dev, prod, local)."""

    name: str
    url: str


ENVIRONMENTS = {
    # "prod": Environment(
    #     name="prod",
    #     url="wss://textualize.io/app-service/",
    # ),
    "local": Environment(
        name="local",
        url="ws://127.0.0.1:8080/app-service/",
    ),
    "dev": Environment(
        name="dev",
        url="wss://textualize-dev.io/app-service/",
    ),
}


def get_environment(environment: str) -> Environment:
    """Get an Environment instance for the given environment name.

    Returns:
        A Environment instance.

    """
    try:
        run_environment = ENVIRONMENTS[environment]
    except KeyError:
        raise RuntimeError(f"Invalid environment {environment!r}")
    return run_environment
