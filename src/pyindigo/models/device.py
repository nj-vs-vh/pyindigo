from enum import Enum, auto

from typing import Dict, Any, Optional

import pyindigo.logging as logging

from ..core.properties import IndigoProperty, TextVectorProperty
from ..core.properties.attribute_enums import IndigoPropertyState
from ..core.properties.schemas import CommonProperties, PropertySchema
from ..core.enums import IndigoDriverAction
from ..core.dispatching_callback import indigo_callback
from ..utils import set_property_with_confirmation


class IndigoDeviceException(Exception):
    pass


class IndigoDeviceStatus(Enum):
    DISCONNECTED = auto()
    CONNECTED = auto()
    FAILED = auto()


class IndigoDevice:
    def __init__(self, name: str, version: str, interface: str):
        self.name = name
        self.version = version
        self.interface = interface
        self.status = IndigoDeviceStatus.DISCONNECTED

        @self.callback(
            accepts={
                "action": IndigoDriverAction.UPDATE,
                "name": CommonProperties.CONNECTION.property_name,
            }
        )
        def connection_status_update(action: IndigoDriverAction, prop: IndigoProperty):
            if prop.state is IndigoPropertyState.OK:
                if prop.items_dict["CONNECTED"]:
                    self.status = IndigoDeviceStatus.CONNECTED
                else:
                    self.status = IndigoDeviceStatus.DISCONNECTED
            elif prop.state is IndigoPropertyState.ALERT:
                if logging.pyindigoConfig.log_device_connection:
                    logging.warning(f"{self.name} connection failed")
                self.status = IndigoDeviceStatus.FAILED

    def __str__(self) -> str:
        return f"{self.name} ({self.version})"

    @classmethod
    def from_info_property(cls, prop: TextVectorProperty):
        if (
            prop.name != CommonProperties.INFO.property_name
        ):  # TODO:  use schemas for all properties!
            raise ValueError(f"Not an INFO property: {prop}")
        items = prop.items_dict
        return cls(
            name=items["DEVICE_NAME"],
            version=items["DEVICE_VERSION"],
            interface=items["DEVICE_INTERFACE"],
        )

    def connect(self, blocking: bool = False, timeout: Optional[float] = None):
        if logging.pyindigoConfig.log_device_connection:
            logging.info(f"Connecting {self.name} device...")
        set_property_with_confirmation(
            prop=CommonProperties.CONNECTION.implement(self.name, CONNECTED=True),
            confirmation=lambda: self.status
            in {IndigoDeviceStatus.CONNECTED, IndigoDeviceStatus.FAILED},
            blocking=blocking,
            timeout=timeout,
        )

    def disconnect(self, blocking: bool = False, timeout: Optional[float] = None):
        if logging.pyindigoConfig.log_device_connection:
            logging.info(f"Disconnecting {self.name} device...")
        set_property_with_confirmation(
            prop=CommonProperties.CONNECTION.implement(self.name, DISCONNECTED=True),
            confirmation=lambda: self.status
            in {IndigoDeviceStatus.DISCONNECTED, IndigoDeviceStatus.FAILED},
            blocking=blocking,
            timeout=timeout,
        )

    def set_property(self, schema: PropertySchema, *args, **kwargs):
        if "device" in kwargs:
            raise ValueError("Deviced cannot be set explicitly when using set_property method")
        if self.status is IndigoDeviceStatus.CONNECTED:
            schema.implement(self.name, *args, **kwargs).set()
        else:
            raise IndigoDeviceException(
                f"Cannot set a property for {self.name} with {self.status.value} status"
            )

    def callback(self, *args, **kwargs):
        """indigo_callback decorator for a specific device"""
        accepts: Dict[str, Any] = kwargs.get("accepts", {})
        accepts.update({"device": self.name})
        return indigo_callback(*args, **kwargs)
