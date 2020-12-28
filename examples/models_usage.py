import time

from pyindigo.models.driver import IndigoDriver
import pyindigo.models.client as client

from pyindigo.core.properties import CCDSpecificProperties, BlobVectorProperty

from pyindigo.enums import IndigoDriverAction, IndigoPropertyState, IndigoLogLevel

import pyindigo.core as indigo
indigo.set_indigo_log_level(IndigoLogLevel.DEBUG)

import pyindigo.logging as logging
logging.pyindigoConfig(False)
logging.basicConfig(level=logging.INFO)


driver = IndigoDriver('indigo_ccd_simulator')
driver.attach()  # will be detached automatically on exit or can be detached manually driver.detach()

time.sleep(1)  # time for device to be defined and registered

print(driver)

simulator = client.find_device('CCD Imager Simulator')

print(f"taking picture with {simulator}")
# output: CCD Imager Simulator (2.0.0.12)

@simulator.callback(
    accepts={
        'name': CCDSpecificProperties.CCD_IMAGE.property_name,
        'state': IndigoPropertyState.OK,
        'property_class': BlobVectorProperty
    }
)
def save_fits(action: IndigoDriverAction, prop: BlobVectorProperty):
    print("writing picture to test.fits")
    with open('test.fits', 'wb') as f:
        f.write(prop.items_dict[CCDSpecificProperties.CCD_IMAGE.allowed_item_names[0]])  # should be IMAGE
    print("success!")

simulator.set_property(CCDSpecificProperties.CCD_EXPOSURE, EXPOSURE=5)
print('waiting for exposure...')

time.sleep(5.5)
