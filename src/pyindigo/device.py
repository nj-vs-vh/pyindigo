from dataclasses import dataclass
from enum import Enum, auto

from typing import Dict, Any, Optional

from .core.properties import IndigoProperty, TextVectorProperty
from .core.properties.attribute_enums import IndigoPropertyState
from .core.properties.schemas import CommonProperties
from .core.enums import IndigoDriverAction
from .core.dispatching_callback import indigo_callback
from .utils import set_property_with_confirmation


class IndigoDeviceStatus(Enum):
    DISCONNECTED = auto()
    CONNECTED = auto()
    FAILED = auto()


@dataclass
class IndigoDevice:
    name: str
    version: str
    interface: str  # TODO: model IndigoInterface for easier property manipulation
    status: IndigoDeviceStatus = IndigoDeviceStatus.DISCONNECTED

    def __post_init__(self):
        @indigo_callback(
            accepts={'action': IndigoDriverAction.UPDATE, 'name': CommonProperties.CONNECTION.property_name}
        )
        def connection_cbk(action: IndigoDriverAction, prop: IndigoProperty):
            if prop.state is IndigoPropertyState.OK:
                if prop.items_dict['CONNECTED']:
                    self.status = IndigoDeviceStatus.CONNECTED
                else:
                    self.status = IndigoDeviceStatus.DISCONNECTED
            else:
                self.status = IndigoDeviceStatus.FAILED

    @classmethod
    def from_driver_info_property(cls, prop: TextVectorProperty):
        if prop.name != 'DRIVER_INFO':  # TODO:  use schemas for all properties!
            raise ValueError(f"Not a DRIVER_INFO property: {prop}")
        items = prop.items_dict
        return cls(name=items['DRIVER_NAME'], version=items['DRIVER_VERSION'], interface=items['DRIVER_INTERFACE'])

    def indigo_callback(self, *args, **kwargs):
        """indigo_callback decorator for specific device"""
        accepts: Dict[str, Any] = kwargs.get('accepts', {})
        accepts.update({'device': self.name})
        return indigo_callback(*args, **kwargs)

    def connect(self, blocking: bool = False, timeout: Optional[float] = None):
        set_property_with_confirmation(
            CommonProperties.CONNECTION.implement(self.name, CONNECTED=True),
            lambda: self.status is IndigoDeviceStatus.CONNECTED,
            blocking, timeout
        )

    def disconnect(self, blocking: bool = False, timeout: Optional[float] = None):
        set_property_with_confirmation(
            CommonProperties.CONNECTION.implement(self.name, DISCONNECTED=True),
            lambda: self.status is IndigoDeviceStatus.CONNECTED,
            blocking, timeout
        )
