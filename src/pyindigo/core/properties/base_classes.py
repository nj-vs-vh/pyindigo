"""Abstract base classes for all Indigo items and properties, see indigo_bus.h"""

from abc import ABC

from typing import ClassVar, Type, Optional

from dataclasses import dataclass

from .property_attributes import IndigoPropertyState, IndigoPropertyPerm, IndigoSwitchRule


@dataclass
class IndigoItem(ABC):
    """Base class for all Indigo items, concrete classes specify data type and representation

    See also indigo_item enum
    """
    name: str
    label: str
    hints: str


@dataclass(repr=False)
class IndigoProperty(ABC):
    """Base class for all Indigo properties, concrete classes must specify item_type"""
    device: str
    name: str
    state: IndigoPropertyState
    perm: IndigoPropertyPerm
    rule: Optional[IndigoSwitchRule] = None
    item_type: ClassVar[Type[IndigoItem]]

    def __post_init__(self):
        # enums are passed from C extension as integers and converted to Python Enums
        self.state = IndigoPropertyState(self.state)
        self.perm = IndigoPropertyPerm(self.perm)
        # item list is always initialized empty and should be built one by one with add_item method
        self.items = []

    def add_rule(self, rule_int: int):
        """Used to specify rule attribute for switch properties"""
        self.rule = IndigoSwitchRule(rule_int)

    def add_item(self, *item_contents):
        """Used to construct property item-by-item from Indigo client callback C code"""
        self.items.append(self.item_type(*item_contents))

    def __repr__(self):
        return (
            f"{self.name} property of '{self.device}' in {self.state.name} state "
            + f"(type={self.__class__.__name__}, perm={self.perm.name}, rule={self.rule.name if self.rule else None})"
        )

    def __str__(self):
        items_repr = '\n'.join('\t' + str(item) for item in self.items)
        return repr(self) + (f'\n\titems:\n{items_repr}' if items_repr else '')
