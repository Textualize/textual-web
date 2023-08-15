from os.path import expandvars

from typing_extensions import Annotated
from pathlib import Path
import tomllib

from pydantic import BaseModel, Field
from pydantic.functional_validators import AfterValidator


ExpandVarsStr = Annotated[str, AfterValidator(expandvars)]


class Account(BaseModel):
    api_key: str | None = None


class App(BaseModel):
    """Defines an application."""

    name: str
    slug: str
    path: ExpandVarsStr
    color: str = ""
    command: ExpandVarsStr = ""
    terminal: bool = False


class Config(BaseModel):
    """Root configuration model."""

    account: Account
    apps: list[App] = Field(default_factory=list)


def default_config() -> Config:
    """Get a default empty configuration.

    Returns:
        Configuration object.
    """
    return Config(account=Account())


def load_config(config_path: Path) -> Config:
    """Load config from a path.

    Args:
        config_path: Path to TOML configuration.

    Returns:
        Config object.
    """
    with Path(config_path).open("rb") as config_file:
        config_data = tomllib.load(config_file)

    config = Config(**config_data)

    return config
