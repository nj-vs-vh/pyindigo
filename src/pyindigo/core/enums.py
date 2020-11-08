"""Various enums representing enumerated data related to Indigo"""

from enum import Enum


class IndigoDriverAction(Enum):
    DEFINE = 'define'
    UPDATE = 'update'
    DELETE = 'delete'


class IndigoLogLevel(Enum):
    ERROR = 0
    INFO = 1
    DEBUG = 2
    TRACE = 3
