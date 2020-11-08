"""Indigo items represent elementary data in Indigo"""

from abc import ABC
from dataclasses import dataclass
from typing import Optional

from .property_attributes import IndigoPropertyState


@dataclass
class IndigoItem(ABC):
    """Base class for all Indigo items, concrete classes specify data type and representation

    See also indigo_item enum
    """
    name: str


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

    def __post_init__(self):
        self.value = float(self.value)

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
        # self.value is passed from C as int, conversion to bool
        self.value = bool(self.value)

    def __str__(self):
        return f'{self.name} = {self.value}'


@dataclass
class LightItem(IndigoItem):
    value: IndigoPropertyState

    def __post_init__(self):
        # self.value is passed from C as int, conversion to IndigoPropertyState
        self.value = IndigoPropertyState(self.value)

    def __str__(self):
        return f'{self.name} is in {self.value.name} state'


@dataclass
class BlobItem(IndigoItem):
    value: bytes
    format: str

    def __str__(self):
        blob_size = len(self.value) if self.value else 0
        return f'{self.name}: {blob_size} bytes ({blob_size / (1024 ** 2):.2f} MB) BLOB in "{self.format}" format'
