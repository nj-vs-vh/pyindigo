import time

import pyindigo.core as core

from properties import TextVectorProperty, NumberVectorProperty, SwitchVectorProperty, LightVectorProperty


print(core.version())

core.setup_client()

core.set_log_level(0)
core.set_property_classes(TextVectorProperty, NumberVectorProperty, SwitchVectorProperty, LightVectorProperty)


def callback(action, prop):
    try:
        print(f"{action}: {str(prop)}")
    except Exception as e:
        print(e)


core.set_dispatching_callback(callback)

core.attach_driver('indigo_ccd_simulator')

time.sleep(3)

core.detach_driver()

time.sleep(3)

core.cleanup_client()
