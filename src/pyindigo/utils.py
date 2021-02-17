import time
from typing import Callable, Optional

from .core.properties import IndigoProperty
import pyindigo.logging as logging


def set_property_with_confirmation(
    prop: IndigoProperty,
    confirmation: Callable[[], bool],
    blocking: bool = False,
    timeout: Optional[float] = None,
):
    if confirmation():
        if logging.pyindigoConfig.log_blocking_property_settings:
            logging.info(
                "set_property_with_confirmation: property is not set because confirmation condition "
                + f"is already satisfied:\n\t{prop}"
            )
        return
    prop.set()
    if blocking:
        waiting_time = 0
        waiting_step = 0.05  # sec
        while not confirmation():
            time.sleep(waiting_step)
            waiting_time += waiting_step
            if timeout is not None and waiting_time > timeout:
                if logging.pyindigoConfig.log_blocking_property_settings:
                    logging.info(
                        f"set_property_with_confirmation: failed on timeout ({timeout} sec):\n\t{prop}"
                    )
                return
        if logging.pyindigoConfig.log_blocking_property_settings:
            logging.info(
                f"set_property_with_confirmation: success, took ~{waiting_time} sec:\n\t{prop}"
            )
