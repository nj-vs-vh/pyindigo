import time

import pyindigo.core as core


print(core.version())

core.setup_client()

core.set_log_level(0)


def callback(action, device_name, property_name):
    print(f"{action}: {device_name} '{property_name}'")


core.set_dispatching_callback(callback)

core.attach_driver('indigo_ccd_simulator')

time.sleep(3)

core.detach_driver()

time.sleep(3)

core.cleanup_client()
