import time

from pyindigo.driver import IndigoDriver


from pyindigo.core.dispatching_callback import set_verbosity
from pyindigo.core import set_indigo_log_level, IndigoLogLevel

set_verbosity(True)
set_indigo_log_level(IndigoLogLevel.TRACE)


driver = IndigoDriver('indigo_ccd_simulator')

driver.attach()

for device in driver.devices:
    print(f'\nconnecting {device}\n')
    device.connect(blocking=True, timeout=3)

print('all devices connected!')

time.sleep(5)

print('end of script, cleanup sequence runs...')
