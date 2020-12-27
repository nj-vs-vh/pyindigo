"""Python side of underlying Indigo client. Module is used as a singleton object with instantiation on first import."""

import atexit

from ..core import setup_client, cleanup_client


setup_client()


drivers = set()

def register_driver(driver):
    drivers.add(driver)


devices = set()

def register_device(device):
    devices.add(device)


def cleanup():
    for device in devices:
        device.disconnect()
    for driver in drivers:
        driver.detach()
    cleanup_client()


def find_device(name: str):
    for equal in (lambda s1, s2: s1.lower() == s2.lower(), lambda s1, s2: s2.lower().startswith(s1.lower())):
        for device in devices:
            if equal(name, device.name):
                return(device)
    else:
        raise ValueError(
            f"No '{name}' device found, available devices are\n\t{'; '.join(dev.name for dev in devices)}"
        )


atexit.register(cleanup)
