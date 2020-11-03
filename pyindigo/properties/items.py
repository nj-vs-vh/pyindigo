"""Concrete classes for different Indigo item types"""

from dataclasses import dataclass
from enum import Enum

from .base_classes import IndigoItem


@dataclass
class TextItem(IndigoItem):
    value: str

    def __str__(self):
        return f'{self.name} = "{self.value}"'


@dataclass
class NumberItem(IndigoItem):
    format: str  # format specifier, see https://en.wikipedia.org/wiki/Printf_format_string#Type_field
    min: float
    max: float
    step: float
    value: float
    target: float

    def __str__(self):
        """Representation for interval with step follows Python slice notation [start:stop:step]"""
        def dtoa(d: float) -> str:
            try:
                return ('{' + self.format.replace('%', ':') + '}').format(d)
            except Exception:
                return str(d)

        return (
            f'{self.name} = {dtoa(self.value)}'
            + f', target {dtoa(self.target)}'
            + f', in range [{dtoa(self.min)}:{dtoa(self.max)}:{dtoa(self.step)}]'
        )


@dataclass
class SwitchItem(IndigoItem):
    value: bool

    def __post_init__(self):
        """self.value is passed from C as int, conversion to bool"""
        self.value = bool(self.value)

    def __str__(self):
        return f'{self.name} = {self.value}'


class IndigoPropertyState(Enum):
    """Mocking indigo_property_state enum from indigo_bus.h, comments are preserved"""
    IDLE = 0  # < property is passive (unused by INDIGO)
    OK = 1  # < property is in correct state or if operation on property was successful
    BUSY = 2  # < property is transient state or if operation on property is pending
    ALERT = 3  # < property is in incorrect state or if operation on property failed


@dataclass
class LightItem(IndigoItem):
    value: IndigoPropertyState

    def __post_init__(self):
        """self.value is passed from C as int, conversion to IndigoPropertyState enum"""
        self.value = IndigoPropertyState(self.value)

    def __str__(self):
        return f'{self.name} is in {self.value.name} state'
