"""Python side of underlying Indigo client. Module is used as a singleton object with instantiation on first import."""

import atexit

from .core import setup_client, cleanup_client


setup_client()


loaded_drivers = []
known_devices = set()


def register_driver(driver):
    loaded_drivers.append(driver)
    known_devices.update(driver.devices)


def detach_all_drivers_and_cleanup():
    for driver in loaded_drivers:
        driver.detach()
    cleanup_client()


atexit.register(detach_all_drivers_and_cleanup)
