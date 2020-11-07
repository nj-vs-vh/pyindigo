import time

import pyindigo.core as indigo
from pyindigo.core.properties import NumberVectorProperty


indigo.setup_client()  # this starts indigo operation

# TODO: model log levels on Python side with Enum
indigo.set_log_level(0)  # 0 = INDIGO_LOG_ERROR


# Dispatching callback is a single Python callable that gets called from all Indigo client
# callbacks. Action type ('define', 'update', 'delete') is passed as first arg, property object as second
# TODO: model action types with Enum
def callback(action, prop):
    try:
        print(f"{action}: {str(prop)}")
    except Exception as e:
        print(e)


indigo.set_dispatching_callback(callback)


indigo.attach_driver('indigo_ccd_simulator')  # currently only one driver at a time is supported

time.sleep(1)  # give driver time to start!

# create property with exposure request and set it (= send it to device)
exposure_prop = NumberVectorProperty('CCD Imager Simulator', 'CCD_EXPOSURE')
exposure_prop.add_item('EXPOSURE', 3.0)
exposure_prop.set()

time.sleep(5)  # wait for exposure

indigo.detach_driver()

time.sleep(3)  # give driver time to gracefully exit

indigo.cleanup_client()
