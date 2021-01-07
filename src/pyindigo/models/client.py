"""Python side of underlying Indigo client. Module is used as a singleton object with instantiation on first import."""

import atexit

from typing import List

from ..core import setup_client, cleanup_client, indigo_callback
from ..core.enums import IndigoDriverAction, IndigoPropertyState
from ..core.properties import IndigoProperty, CommonProperties

from .device import IndigoDevice
from .driver import IndigoDriver


setup_client()


drivers: List[IndigoDriver] = []


def register_driver(driver: IndigoDriver):
    drivers.append(driver)


@indigo_callback(
    accepts={
        'action': IndigoDriverAction.DEFINE,
        'name': CommonProperties.INFO.property_name,
        'state': IndigoPropertyState.OK,
    }
)
def register_device_callback(_, prop: IndigoProperty):
    register_device(IndigoDevice.from_info_property(prop))


devices: List[IndigoDevice] = []


def register_device(device: IndigoDriver):
    devices.append(device)


@atexit.register
def cleanup():
    for device in devices:
        device.disconnect(blocking=True)
    for driver in drivers:
        driver.detach()
    cleanup_client()


def find_device(name: str) -> IndigoDevice:  # noqa
    for equal in (lambda s1, s2: s1.lower() == s2.lower(), lambda s1, s2: s2.lower().startswith(s1.lower())):
        for device in devices:
            if equal(name, device.name):
                return(device)
    else:
        raise ValueError(
            f"No '{name}' device found, available devices are: \n\t{'; '.join(dev.name for dev in devices)}"
        )
