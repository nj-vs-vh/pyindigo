"""Core Pyindigo functionality.

This package incapsulates
    (a) C extension module pyindigo.core_ext that actually runs Indigo bus and sends indigo messages.
    (b) Python classes representing Indigo items and properties that are constructed and returned by C extension

Pyindigo users should import all functions from this module and not from core_ext.
"""

# flake8: noqa

from .properties import TextVectorProperty, NumberVectorProperty, SwitchVectorProperty, LightVectorProperty, BlobVectorProperty

from .core_ext import *

set_property_classes(TextVectorProperty, NumberVectorProperty, SwitchVectorProperty, LightVectorProperty, BlobVectorProperty)

# dummy callback just to replace NULL in C code
set_dispatching_callback(lambda action, property: None)


# not necessary but advised for linting purposes
__all__ = [
    'setup_client',
    'cleanup_client',
    'set_log_level',
    'set_property_classes',
    'attach_driver',
    'detach_driver',
    'set_dispatching_callback',
    'disconnect_device',
]
