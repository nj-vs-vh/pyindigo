import time

# be careful! Indigo thread starts right here at the moment you import anything from models subpackage!
from pyindigo.models.driver import IndigoDriver
import pyindigo.models.client as client

from pyindigo.core.properties import CCDSpecificProperties, BlobVectorProperty
from pyindigo.core.enums import IndigoDriverAction, IndigoPropertyState

import pyindigo.logging as logging
logging.basicConfig(filename='pyindigo.log', level=logging.DEBUG)
logging.pyindigoConfig(log_driver_actions=True, log_device_connection=True, log_blocking_property_settings=True)


driver = IndigoDriver('indigo_ccd_simulator')
driver.attach()  # will be detached automatically on exit or can be detached manually driver.detach()

time.sleep(1)  # time for device to be defined and registered

print(f"current driver: {driver}")

simulator = client.find_device('CCD Imager Simulator')

simulator.connect(blocking=True)

print(f"taking picture with device {simulator}")
# expected result: CCD Imager Simulator (2.0.0.12)


@simulator.callback(
    accepts={
        'action': IndigoDriverAction.UPDATE,
        'name': CCDSpecificProperties.CCD_IMAGE.property_name,
        'state': IndigoPropertyState.OK,
        'property_class': BlobVectorProperty,
    }
)
def save_fits(action: IndigoDriverAction, prop: BlobVectorProperty):
    print("writing picture to test.fits")
    with open('test.fits', 'wb') as f:
        f.write(prop.items_dict[CCDSpecificProperties.CCD_IMAGE.allowed_item_names[0]])
    print("success!")


simulator.set_property(CCDSpecificProperties.CCD_EXPOSURE, EXPOSURE=5)
print('waiting for exposure...')

time.sleep(5.5)
