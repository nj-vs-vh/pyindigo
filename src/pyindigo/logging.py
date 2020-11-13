"""Custom logging module wrapping standard logging, but with custon config options

Intended use:
>>> import pyindigo.logging as logging
>>> logging.basicConfig(filename='pyindigo.log', encoding='utf-8', level=logging.DEBUG)
>>> logging.pyindigoConfig(log_driver_actions=True, log_property_set=True)
>>> logging.warn("Beware!")
>>> logging.debug("Some details here")
"""

from logging import *  # noqa

import inspect


class pyindigoConfig:
    # used with logger.info and True by default
    log_property_set: bool = False
    log_driver_actions: bool = False
    log_callback_dispatching: bool = False
    log_device_connection: bool = False

    # used with logger.warning and True by default
    lop_callback_exceptions: bool = True
    log_alert_properties: bool = True

    def __new__(cls, *args, **kwargs):
        """Not an actual instantiation, but setting class attributes, mocking logging.basicConfig"""
        if len(args) == 1 and isinstance(args[0], bool):
            for name, flag in inspect.getmembers(cls, lambda val: isinstance(val, bool)):
                setattr(cls, name, args[0])
        if len(args) > 1:
            raise ValueError("Only one positional argument can be set (all flags at once)")
        for key, val in kwargs.items():
            if not hasattr(cls, key):
                raise KeyError(f"Unknown logging option {key}={val}")
            setattr(cls, key, val)
