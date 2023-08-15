from os.path import expandvars

from typing_extensions import Annotated
from pathlib import Path
import tomllib

from pydantic import BaseModel, Field
from pydantic.functional_validators import AfterValidator


ExpandVarsStr = Annotated[str, AfterValidator(expandvars)]


class Account(BaseModel):
    domain: str | None = None
    api_key: str | None = None


class App(BaseModel):
    name: str
    slug: str
    color: str = ""
    path: ExpandVarsStr
    command: ExpandVarsStr = ""
    terminal: bool = False


class Config(BaseModel):
    account: Account
    apps: list[App] = Field(default_factory=list)


def default_config() -> Config:
    """Get a default config."""
    return Config(account=Account())


def load_config(config_path: Path) -> Config:
    """Load config from path."""
    with Path(config_path).open("rb") as config_file:
        config_data = tomllib.load(config_file)

    config = Config(**config_data)

    return config
