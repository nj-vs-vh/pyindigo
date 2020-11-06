"""Concrete classes for different Indigo item types"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .base_classes import IndigoItem


@dataclass
class TextItem(IndigoItem):
    value: str

    def __str__(self):
        return f'{self.name} = "{self.value}"'


@dataclass
class NumberItem(IndigoItem):
    value: float
    format: str = r'%g'  # format specifier, see https://en.wikipedia.org/wiki/Printf_format_string#Type_field
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None
    target: Optional[float] = None

    def __str__(self):
        def dtoa(d: float) -> str:
            try:
                return ('{' + self.format.replace('%', ':') + '}').format(d)
            except Exception:
                return str(d)

        return (
            f'{self.name} = {dtoa(self.value)}'
            + f', target {dtoa(self.target)}'
            # representation for interval with step follows Python slice notation [min:max:step]
            + f', in range [{dtoa(self.min)}:{dtoa(self.max)}:{dtoa(self.step)}]'
        )


@dataclass
class SwitchItem(IndigoItem):
    value: bool

    def __post_init__(self):
        """self.value is passed from C as int, conversion to bool is done"""
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
        """self.value is passed from C as int, conversion to IndigoPropertyState"""
        self.value = IndigoPropertyState(self.value)

    def __str__(self):
        return f'{self.name} is in {self.value.name} state'


@dataclass
class BlobItem(IndigoItem):
    value: bytes
    format: str

    def __str__(self):
        return f'{len(self.value or [])} bytes BLOB {self.name} in "{self.format}" format'
