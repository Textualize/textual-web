from typing import NewType


AppID = NewType("AppID", str)
Meta = dict[str, str | None | int | bool]
RouteKey = NewType("RouteKey", str)
SessionID = NewType("SessionID", str)
