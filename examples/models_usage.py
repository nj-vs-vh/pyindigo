import time

from pyindigo.models.driver import IndigoDriver
import pyindigo.models.client as client

from pyindigo.core.properties import CCDSpecificProperties, BlobVectorProperty
from pyindigo.enums import IndigoDriverAction, IndigoPropertyState

import pyindigo.logging as logging
logging.pyindigoConfig(False)
logging.basicConfig(level=logging.INFO)


driver = IndigoDriver('indigo_ccd_simulator')
driver.attach()  # will be detached automatically on exit

time.sleep(0.5)  # time for device to be defined and registered

simulator = client.find_device('CCD Imager Simulator')

print(f"taking picture with {simulator}")
# output: CCD Imager Simulator (2.0.0.12)

@simulator.callback(
    accepts={
        'name': 'CCD1',  # probably a bug in CCD Simulator, should be CCD_IMAGE
        'state': IndigoPropertyState.OK,
        'property_class': BlobVectorProperty
    }
)
def save_fits(action: IndigoDriverAction, prop: BlobVectorProperty):
    print("writing picture to test.fits")
    with open('test.fits', 'wb') as f:
        f.write(prop.items_dict['CCD1'])  # should be IMAGE
    print("success!")

simulator.set_property(CCDSpecificProperties.CCD_EXPOSURE, EXPOSURE=5)
print('waiting for exposure...')

time.sleep(5.5)
