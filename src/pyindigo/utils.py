import time
from typing import Callable, Optional

from .core.properties import IndigoProperty


def set_property_with_confirmation(
    prop: IndigoProperty, confirmation: Callable[[], bool], blocking: bool = False, timeout: Optional[float] = None
):
    if confirmation():
        return
    prop.set()
    if blocking:
        waiting_time = 0
        waiting_step = 0.1  # sec
        while not confirmation():
            time.sleep(waiting_step)
            waiting_time += waiting_step
            if timeout is not None and waiting_time > timeout:
                break
