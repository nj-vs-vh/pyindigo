import time

import pyindigo.core as indigo

from pyindigo.core.properties import CommonProperties, CCDSpecificProperties
from pyindigo.core import indigo_callback
from pyindigo.enums import IndigoDriverAction, IndigoLogLevel


# print only updates by CCD Imager Simulator
@indigo_callback(accepts={'action': IndigoDriverAction.UPDATE, 'device': 'CCD Imager Simulator'})
def print_property(action, prop):
    print(f"{action.value}: {prop}")


indigo.setup_client()  # this starts indigo operation

indigo.set_indigo_log_level(IndigoLogLevel.ERROR)

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
# this usage of schema is equivalent (but much more convenient) to this code:
# prop = NumberVectorProperty('CCD Imager Simulator', 'CCD_EXPOSURE')
# prop.add_item('EXPOSURE', 3.0)
# prop.set()

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
