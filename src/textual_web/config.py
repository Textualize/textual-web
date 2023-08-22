from os.path import expandvars
from typing import Optional, Dict, List

from typing_extensions import Annotated
from pathlib import Path
import tomli


from pydantic import BaseModel, Field
from pydantic.functional_validators import AfterValidator

from .identity import generate
from .slugify import slugify

ExpandVarsStr = Annotated[str, AfterValidator(expandvars)]


class Account(BaseModel):
    api_key: Optional[str] = None


class App(BaseModel):
    """Defines an application."""

    name: str
    slug: str = ""
    path: ExpandVarsStr = "./"
    color: str = ""
    command: ExpandVarsStr = ""
    terminal: bool = False


class Config(BaseModel):
    """Root configuration model."""

    account: Account
    apps: List[App] = Field(default_factory=list)


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
        config_data = tomli.load(config_file)

    account = Account(**config_data.get("account", {}))

    def make_app(name, data: Dict[str, object], terminal: bool = False) -> App:
        data["name"] = name
        data["terminal"] = terminal
        if terminal:
            data["slug"] = generate().lower()
        elif not data.get("slug", ""):
            data["slug"] = slugify(name)

        return App(**data)

    apps = [make_app(name, app) for name, app in config_data.get("app", {}).items()]

    apps += [
        make_app(name, app, terminal=True)
        for name, app in config_data.get("terminal", {}).items()
    ]

    config = Config(account=account, apps=apps)

    return config
