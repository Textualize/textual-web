from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Environment:
    """Data structure to describe the environment (dev, prod, local)."""

    name: str
    api_url: str
    url: str


ENVIRONMENTS = {
    # "prod": Environment(
    #     name="prod",
    #     url="wss://textualize.io/app-service/",
    # ),
    "local": Environment(
        name="local",
        api_url="ws://127.0.0.1:8080/api/",
        url="ws://127.0.0.1:8080/app-service/",
    ),
    "dev": Environment(
        name="dev",
        api_url="https://textualize-dev.io/api",
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
