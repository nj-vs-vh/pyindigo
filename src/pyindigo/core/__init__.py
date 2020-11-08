"""Core Pyindigo functionality.

This package incapsulates
    (a) C extension module pyindigo.core_ext that actually runs Indigo bus and sends indigo messages.
    (b) Python classes representing Indigo items and properties that are constructed and returned by C extension

Pyindigo users should import all functions from this module and not from core_ext.
"""

# flake8: noqa

# other core_ext functions are not meant to be exposed to the user
from .core_ext import setup_client, cleanup_client, attach_driver, detach_driver, disconnect_device


# setting up links to pyindigo.core objects and functions in core_ext...

from .core_ext import set_property_classes as _set_property_classes
from .properties.properties import TextVectorProperty, NumberVectorProperty, SwitchVectorProperty, LightVectorProperty, BlobVectorProperty
_set_property_classes(TextVectorProperty, NumberVectorProperty, SwitchVectorProperty, LightVectorProperty, BlobVectorProperty)

from .core_ext import set_dispatching_callback as _set_dispatching_callback
from .dispatching_callback import dispatching_callback
_set_dispatching_callback(dispatching_callback)

from .core_ext import set_log_level as _set_log_level
from .enums import IndigoLogLevel as LogLevel
def set_indigo_log_level(log_level: LogLevel):
    _set_log_level(log_level.value)


# not necessary but used for linting purposes
__all__ = [
    'setup_client',
    'cleanup_client',
    'LogLevel',
    'set_indigo_log_level',
    'attach_driver',
    'detach_driver',
    'disconnect_device',
]
