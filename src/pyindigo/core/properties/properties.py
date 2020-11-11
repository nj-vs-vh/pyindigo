"""Indigo properties represent messages sent to and received from Indigo devices, they contain lists of items"""

from dataclasses import dataclass

from abc import ABC

from typing import ClassVar, Type, Optional

from .attribute_enums import IndigoPropertyState, IndigoPropertyPerm, IndigoSwitchRule
from .items import IndigoItem, TextItem, NumberItem, SwitchItem, LightItem, BlobItem

from ..core_ext import set_property


@dataclass(repr=False)
class IndigoProperty(ABC):
    """Base class for all Indigo properties, concrete classes must specify item_type"""
    device: str
    name: str
    state: Optional[IndigoPropertyState] = None
    perm: Optional[IndigoPropertyPerm] = None
    rule: Optional[IndigoSwitchRule] = None
    item_type: ClassVar[Type[IndigoItem]]

    def __post_init__(self):
        # enums are passed from C extension as integers and converted to Python Enums
        self.state = IndigoPropertyState(self.state) if self.state is not None else None
        self.perm = IndigoPropertyPerm(self.perm) if self.perm is not None else None
        # item list is always initialized empty and should be built one by one with add_item method
        self.items = []

    def add_item(self, *item_contents):
        """Used to construct property item-by-item from Indigo client callback C code"""
        self.items.append(self.item_type(*item_contents))

    def __repr__(self):
        return (
            f"{self.name} property of '{self.device}' in {self.state.name if self.state else 'UNKNOWN'} state "
            + f"(type={self.__class__.__name__}, "
            + f"perm={self.perm.name if self.perm else 'UNKNOWN'}, "
            + f"rule={self.rule.name if self.rule else None})"
        )

    def __str__(self):
        items_repr = '\n'.join('\t' + str(item) for item in self.items)
        return repr(self) + (f'\n\titems:\n{items_repr}' if items_repr else '')

    @property
    def items_dict(self):
        return {item.name: item.value for item in self.items}

    def set(self):
        """Request for change corresponding Indigo property to match self"""
        if not self.items:
            raise ValueError("Cannot set empty property, call add_item at least once!")
        set_property(
            self.device, self.name, self.__class__,
            [item.name for item in self.items],
            [item.value for item in self.items]
        )


@dataclass(repr=False)
class TextVectorProperty(IndigoProperty):
    item_type = TextItem


@dataclass(repr=False)
class NumberVectorProperty(IndigoProperty):
    item_type = NumberItem


@dataclass(repr=False)
class SwitchVectorProperty(IndigoProperty):
    item_type = SwitchItem

    def add_rule(self, rule_int: int):
        """Used to specify rule attribute for switch properties"""
        self.rule = IndigoSwitchRule(rule_int)

    def __str__(self):
        on_item_names = ', '.join(item.name for item in self.items if item.value)
        off_item_names = ', '.join(item.name for item in self.items if not item.value)
        return (
            repr(self)
            + ('\n\tOn: ' + on_item_names if on_item_names else '')
            + ('\n\tOff: ' + off_item_names if off_item_names else '')
        )


@dataclass(repr=False)
class LightVectorProperty(IndigoProperty):
    item_type = LightItem


@dataclass(repr=False)
class BlobVectorProperty(IndigoProperty):
    item_type = BlobItem
