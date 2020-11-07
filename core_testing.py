import time

import pyindigo.core as indigo
from pyindigo.core.properties import NumberVectorProperty


indigo.setup_client()

indigo.set_log_level(0)


def callback(action, prop):
    try:
        print(f"{action}: {str(prop)}")
    except Exception as e:
        print(e)


indigo.set_dispatching_callback(callback)

indigo.attach_driver('indigo_ccd_simulator')

time.sleep(3)

exposure_prop = NumberVectorProperty('CCD Imager Simulator', 'CCD_EXPOSURE')
exposure_prop.add_item('EXPOSURE', 3.0)
exposure_prop.set()

time.sleep(5)

indigo.detach_driver()

time.sleep(3)

indigo.cleanup_client()
