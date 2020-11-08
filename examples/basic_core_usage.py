import time

import pyindigo.core as indigo
from pyindigo.core.properties.schemas import CommonProperties, CCDSpecificProperties


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

# sleep 1 sec after every operation to prevent deadlocks and races, giving Indigo time to respond
# this should normally be done with some kind of async callback processing
time.sleep(1)

# connect CCD Imager Simulator and focuser by creating connection property object and setting it (= sending to device)
prop = CommonProperties.CONNECTION.implement('CCD Imager Simulator', CONNECTED=True)
print('='*10)
print(f'setting {prop}')
print('='*10)
prop.set()
time.sleep(1)

prop = CommonProperties.CONNECTION.implement('CCD Imager Simulator (focuser)', CONNECTED=True)
print('='*10)
print(f'setting {prop}')
print('='*10)
prop.set()
time.sleep(1)

# create property with exposure request and set it
prop = CCDSpecificProperties.CCD_EXPOSURE.implement('CCD Imager Simulator', 4)
print('='*10)
print(f'setting {prop}')
print('='*10)
prop.set()
time.sleep(1)
# this usage of schema is equivalent (but much more convenient than) to this code:
# exposure_prop = NumberVectorProperty('CCD Imager Simulator', 'CCD_EXPOSURE')
# exposure_prop.add_item('EXPOSURE', 3.0)
# exposure_prop.set()

# disconnect focuser as we don't use it now
prop = CommonProperties.CONNECTION.implement('CCD Imager Simulator (focuser)', DISCONNECTED=True)
print('='*10)
print(f'setting {prop}')
print('='*10)
prop.set()

time.sleep(5)  # wait for exposure

indigo.detach_driver()

time.sleep(3)  # give driver time to gracefully exit

indigo.cleanup_client()
