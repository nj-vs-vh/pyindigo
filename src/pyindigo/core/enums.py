"""Various enums representing enumerated data related to Indigo"""

from enum import Enum

from .properties.attribute_enums import IndigoPropertyPerm, IndigoPropertyState, IndigoSwitchRule


class IndigoDriverAction(Enum):
    DEFINE = "define"
    UPDATE = "update"
    DELETE = "delete"

    def __str__(self):
        return self.value


class IndigoLogLevel(Enum):
    ERROR = 0
    INFO = 1
    DEBUG = 2
    TRACE = 3


__all__ = [
    "IndigoPropertyPerm",
    "IndigoPropertyState",
    "IndigoSwitchRule",
    "IndigoDriverAction",
    "IndigoLogLevel",
]
