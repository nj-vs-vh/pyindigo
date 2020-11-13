import time

from pyindigo.driver import IndigoDriver
from pyindigo.core.properties import IndigoProperty, CCDSpecificProperties
from pyindigo.enums import IndigoPropertyState, IndigoDriverAction, IndigoDeviceStatus

import pyindigo.logging as logging
logging.pyindigoConfig(True)
logging.basicConfig(level=logging.INFO)


driver = IndigoDriver('indigo_ccd_simulator')

driver.attach()

print('\ndriver attached!\n')

imager = driver.find_device('CCD Imager Simulator')
imager.connect(blocking=True, timeout=5)

if imager.status is not IndigoDeviceStatus.CONNECTED:
    exit()

# for device in driver.devices:
#     print(f'\nconnecting {device}\n')
#     device.connect(blocking=True, timeout=3)

print('\ndevice connected!\n')

image_saved = False


@imager.indigo_callback(
    accepts={
        'state': IndigoPropertyState.OK,
        'action': IndigoDriverAction.UPDATE,
        'property_class': CCDSpecificProperties.CCD_FRAME.property_class
    }
)
def save_image_to_file(action, prop: IndigoProperty):
    try:
        print('saving image...')
        with open('test.fits', 'wb') as f:
            f.write(prop.items[0].value)
    except Exception:
        pass
    finally:
        global image_saved
        image_saved = True


CCDSpecificProperties.CCD_EXPOSURE.implement(imager.name, 5).set()


while not image_saved:
    time.sleep(0.1)

print('end of script, cleanup sequence runs...')
