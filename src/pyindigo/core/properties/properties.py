from dataclasses import dataclass

from .base_classes import IndigoProperty

from .items import TextItem, NumberItem, SwitchItem, LightItem


@dataclass(repr=False)
class TextVectorProperty(IndigoProperty):
    item_type = TextItem


@dataclass(repr=False)
class NumberVectorProperty(IndigoProperty):
    item_type = NumberItem


@dataclass(repr=False)
class SwitchVectorProperty(IndigoProperty):
    item_type = SwitchItem

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
