"""Core Pyindigo functionality.

This package incapsulates
    (a) C extension module pyindigo.core.core_ext that actually runs Indigo bus and transmits Indigo messages.
    (b) Python classes representing Indigo items and properties that are constructed and returned by C extension
    (c) Dispatching callback

Pyindigo users should import all functions from this module and not from core_ext.
"""

# flake8: noqa

# other core_ext functions are not meant to be exposed to the user
from .core_ext import setup_client, cleanup_client, attach_driver, detach_driver, disconnect_device


# setting up links to pyindigo.core objects and functions in core_ext...

from .core_ext import set_property_classes as _set_property_classes
from .properties.properties import (
    TextVectorProperty,
    NumberVectorProperty,
    SwitchVectorProperty,
    LightVectorProperty,
    BlobVectorProperty,
)

_set_property_classes(
    TextVectorProperty,
    NumberVectorProperty,
    SwitchVectorProperty,
    LightVectorProperty,
    BlobVectorProperty,
)

from .core_ext import set_dispatching_callback as _set_dispatching_callback
from .dispatching_callback import dispatching_callback

_set_dispatching_callback(dispatching_callback)

from .core_ext import set_log_level as _set_log_level
from .enums import IndigoLogLevel


def set_indigo_log_level(log_level: IndigoLogLevel = IndigoLogLevel.ERROR):
    _set_log_level(log_level.value)


from .dispatching_callback import indigo_callback


# not necessary but used for linting purposes
__all__ = [
    "set_indigo_log_level",
    "setup_client",
    "cleanup_client",
    "attach_driver",
    "detach_driver",
    "disconnect_device",
    "indigo_callback",
]
