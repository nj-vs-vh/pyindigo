"""Property attribute enumerations modeled with Python Enums, see indigo_bus.h"""

from enum import Enum


class IndigoPropertyState(Enum):
    """indigo_property_state"""

    IDLE = 0  # < property is passive (unused by INDIGO)
    OK = 1  # < property is in correct state or if operation on property was successful
    BUSY = 2  # < property is transient state or if operation on property is pending
    ALERT = 3  # < property is in incorrect state or if operation on property failed


class IndigoPropertyPerm(Enum):
    """indigo_property_perm"""

    RO = 1  # < read-only
    RW = 2  # < read-write
    WO = 3  # < write-only


class IndigoSwitchRule(Enum):
    """indigo_rule"""

    EXACTLY_ONE = 1  # < radio button group like behaviour with one switch in "on" state
    AT_MOST_ONE = 2  # < radio button group like behaviour with none or one switch in "on" state
    ANY = 3  # < checkbox button group like behaviour
