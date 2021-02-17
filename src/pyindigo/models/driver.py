"""Class representing Indigo driver and helper functions. Currently is just a placeholder"""

from ..core import attach_driver, detach_driver


class IndigoDriver:
    def __init__(self, driver_lib_name: str):
        # importing here to avoid circular import
        from .client import register_driver

        self._register_driver = register_driver

        self.driver_lib_name = driver_lib_name
        self.attached = False

    def __str__(self) -> str:
        return f"{self.driver_lib_name} ({'not' if not self.attached else ''}attached)"

    def attach(self):
        attach_driver(self.driver_lib_name)
        # this line sends attached driver to client for later automatical detachment
        self._register_driver(self)
        self.attached = True

    def detach(self):
        if self.attached:
            # after several drivers support this will be something like detach_driver(self.driver_lib_name)
            detach_driver()
            self.attached = False
