from typing import NewType, Union, Dict


AppID = NewType("AppID", str)
Meta = Dict[str, Union[str, None, int, bool]]
RouteKey = NewType("RouteKey", str)
SessionID = NewType("SessionID", str)
