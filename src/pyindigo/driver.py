"""Class representing Indigo driver and helper functions"""

import time
from dataclasses import dataclass, field

from typing import Optional, List

from .core import attach_driver, detach_driver
from .core.dispatching_callback import indigo_callback, discard_indigo_callback
from .core.properties import IndigoProperty
from .core.properties.attribute_enums import IndigoPropertyState
from .core.enums import IndigoDriverAction

from .client import register_driver
from .device import IndigoDevice


@dataclass
class IndigoDriver:
    driver_lib_name: str
    devices: List[IndigoDevice] = field(default_factory=list)
    attached: bool = False

    def attach(self, time_window: Optional[int] = 1):
        driver_info_props = []

        @indigo_callback(
            accepts={'action': IndigoDriverAction.DEFINE, 'name': 'DRIVER_INFO', 'state': IndigoPropertyState.OK}
        )
        def add_device_callback(_, prop: IndigoProperty):
            driver_info_props.append(prop)

        attach_driver(self.driver_lib_name)
        self.attached = True
        if time_window:
            time.sleep(time_window)
            discard_indigo_callback(add_device_callback)
        register_driver(self)
        for prop in driver_info_props:
            self.devices.append(IndigoDevice.from_driver_info_property(prop))

    def detach(self):
        if self.attached:
            for device in self.devices:
                device.disconnect(blocking=True, timeout=3)
            # detach_driver(self.driver_lib_name)
            detach_driver()
            self.attached = False


if __name__ == "__main__":
    driver = IndigoDriver('indigo_ccd_simulator')
    time.sleep(1)
    print(driver.devices)
