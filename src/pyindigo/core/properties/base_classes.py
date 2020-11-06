"""Abstract base classes for all Indigo items and properties"""

from abc import ABC

from typing import ClassVar, Type

from dataclasses import dataclass


@dataclass
class IndigoItem(ABC):
    """Base class for all Indigo items"""
    name: str
    label: str
    hints: str


@dataclass(repr=False)
class IndigoProperty(ABC):
    name: str
    device: str
    item_type: ClassVar[Type[IndigoItem]]

    def __post_init__(self):
        """Item list is always initialized empty and should be built one by one with add_item method"""
        self.items = []

    def add_item(self, *item_contents):
        """Used to construct property item-by-item from Indigo client callback C code"""
        self.items.append(self.item_type(*item_contents))

    def __repr__(self):
        return f"{self.name} property of {self.device} ({self.__class__.__name__})"

    def __str__(self):
        items_repr = '\n'.join('\t' + str(item) for item in self.items)
        return repr(self) + (f'; items:\n{items_repr}' if items_repr else '')
