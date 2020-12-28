"""Class representing Indigo driver and helper functions. Currently is just a placeholder"""

import time

from typing import Optional, List

from ..core import attach_driver, detach_driver
from ..core.dispatching_callback import indigo_callback, discard_indigo_callback
from ..core.properties import IndigoProperty
from ..core.properties.attribute_enums import IndigoPropertyState
from ..core.enums import IndigoDriverAction

from .client import register_driver
from .device import IndigoDevice


class IndigoDriver:
    def __init__(self, driver_lib_name: str):
        self.driver_lib_name = driver_lib_name
        self.attached = False

    def __str__(self) -> str:
        return f"{self.driver_lib_name} ({'not' if not self.attached else ''}attached)"

    def attach(self):
        attach_driver(self.driver_lib_name)
        register_driver(self)
        self.attached = True

    def detach(self):
        if self.attached:
            # detach_driver(self.driver_lib_name)
            detach_driver()
            self.attached = False
