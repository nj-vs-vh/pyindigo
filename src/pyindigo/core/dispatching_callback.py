"""Dispatching callback is a single Python callable invoked from C code to process all properties"""

from dataclasses import dataclass, fields
from typing import Optional, Callable, List, Dict, Any
from asyncio import AbstractEventLoop, run_coroutine_threadsafe
from inspect import iscoroutine
from warnings import warn

from .properties.properties import IndigoProperty
from .properties.attribute_enums import IndigoPropertyState, IndigoPropertyPerm, IndigoSwitchRule
from .enums import IndigoDriverAction


IndigoCallback = Callable[[IndigoDriverAction, IndigoProperty], None]


@dataclass
class IndigoCallbackEntry:
    """Callback + info on when and how to run it"""
    callback: IndigoCallback

    action: Optional[IndigoDriverAction] = None
    property_class: Optional[IndigoProperty] = None

    device: Optional[str] = None
    name: Optional[str] = None
    state: Optional[IndigoPropertyState] = None
    perm: Optional[IndigoPropertyPerm] = None
    rule: Optional[IndigoSwitchRule] = None

    run_times: Optional[int] = None  # None = no limit on how many times callback is run
    loop: Optional[AbstractEventLoop] = None

    def __post_init__(self):
        if not callable(self.callback):
            raise RuntimeError(f"Unable to register {self.callback} - not a callable!")
        if iscoroutine(self.callback) and self.loop is None:
            raise ValueError("loop parameter must be specified when registering coroutines!")
        if not iscoroutine(self.callback) and self.loop is not None:
            warn("loop parameter is specified, but registered callable is not a coroutine!")

    def accepts(self, action: IndigoDriverAction, prop: IndigoProperty) -> bool:
        if self.action is not None and action is not self.action:
            return False
        if self.property_class is not None and prop.__class__ is not self.property_class:
            return False
        for field in fields(prop):
            desired_value = getattr(self, field.name, None)
            property_value = getattr(prop, field.name, None)
            if desired_value is not None and property_value != desired_value:
                return False
        return True

    def run_if_applied(self, action: IndigoDriverAction, prop: IndigoProperty):
        if self.accepts(action, prop):
            try:
                if iscoroutine(self.callback):
                    run_coroutine_threadsafe(self.callback(action, prop), self.loop)
                else:
                    self.callback(action, prop)
            except Exception:
                pass
            finally:
                if self.run_times is not None:
                    self.run_times -= 1


registered_callbacks: List[IndigoCallbackEntry] = []


def dispatching_callback(action_string: str, prop: IndigoProperty):
    global registered_callbacks
    action = IndigoDriverAction(action_string)
    for i, callback_entry in enumerate(registered_callbacks):
        callback_entry.run_if_applied(action, prop)
    registered_callbacks = [entry for entry in registered_callbacks if entry.run_times is None or entry.run_times > 0]


def indigo_callback(
    callback: Optional[IndigoCallback] = None,
    /, *,
    accepts: Optional[Dict[str, Any]] = {},
    run_times: Optional[int] = None,
    loop: Optional[AbstractEventLoop] = None
):
    """Main decorator/decorator factory for managing Indigo callbacks.

    Basic usage:
    >>> @indigo_callback
    >>> def my_callback(action: IndigoDriverAction, prop: IndigoProperty):
    >>>     ...

    Passes all driver actions and properties from Indigo to my_callback. This do not affect other callbacks,
    i.e. all registered callbacks are run, but order is not guaranteed. Errors generated in callbacks do not
    propagate, so do your own error handling in callbacks.

    Usage with parameters:
    >>> @indigo_callback(
    >>>     accepts={
    >>>         'device': 'CCD Imager simulator',
    >>>         'name': CommonProperties.CONNECTION.property_name,
    >>>         'state': IndigoPropertyState.OK
    >>>    },
    >>>    run_times=3
    >>> )
    >>> def my_selective_callback(action: IndigoDriverAction, prop: IndigoProperty):
    >>>     ...

    Basic action/property filtering is done by the dispatching callback, and my_selective_callback runs only when driver
    action and property attributes match those passed to indigo_callback decorator factory. Non-specified field mean
    any value is acceptable.
    Additional optional arguments:
        run_times specifies how many times callback will be run before being discarded;
        loop, if coroutine is decorated, specifies asyncio loop to run it in.
    """
    # TODO: support 'accepts' as a List if possible (i.e. for accept=[IndigoPropertyState.OK, IndigoPropertyPerm.RO])

    def decorator(decorated_callback):
        registered_callbacks.append(IndigoCallbackEntry(decorated_callback, **accepts, run_times=run_times, loop=loop))
        return decorated_callback

    if callback is None:  # when using as decorator factory
        return decorator
    else:  # when using as decorator
        return decorator(callback)
