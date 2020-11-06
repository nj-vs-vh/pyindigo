from enum import Enum

import _pyindigo


class IndigoVerbosity(Enum):
    """indigo_log_levels enumeration from indigo_bus.c modelled with integer verbosity levels"""
    ERRORS = 0
    INFO = 1
    DEBUG = 2
    TRACE = 3


class _IndigoClient:
    """Class representing INDIGO client, i.e. the whole pyindigo module, stores list of attached INDIGO drivers.

    Attempt to instantiate it from outside of this module will raise RuntimeError, because there cannot be more
    than one client at once. Outside users should import indigo_client instance.

    Reason for it to be a class is a convention to keep cleanup code in __del__ method, even though it's executed
    only at the end of the program, when module level instance is destroyed
    """

    _indigo_client_exists = False

    def __new__(cls, *args, **kwargs):
        if cls._indigo_client_exists:
            raise RuntimeError("Attempt to create more than one INDIGO client!")
        cls._indigo_client_exists = True
        return super().__new__(cls)

    def __init__(self, verbosity: IndigoVerbosity):
        _pyindigo.setup_indigo_client(verbosity.value)
        self.attached_drivers = []

    def __del__(self):
        for driver in self.attached_drivers:
            driver.detach()
        _pyindigo.cleanup_indigo_client()


indigo_client = _IndigoClient(IndigoVerbosity.TRACE)


__all__ = ['indigo_client']
