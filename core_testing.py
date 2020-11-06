import time

import pyindigo.core as indigo

import pyindigo.core_ext as core_ext


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

core_ext.take_shot()

time.sleep(5)

indigo.detach_driver()

time.sleep(3)

indigo.cleanup_client()
