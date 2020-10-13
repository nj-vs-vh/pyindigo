import _pyindigo
from astropy.io.fits import HDUList

import time


def save_bytes_to_file(b: bytes = None) -> None:
    try:
        global file_written
        hdul = HDUList.fromstring(b)
        hdul.writeto('astropy_temp.fits')
    except Exception as e:
        print(f'error occured in callback: {e}')
    file_written = True


_pyindigo.set_device_name("CCD Imager Simulator")
_pyindigo.get_current_device_name()

_pyindigo.setup_ccd_client("indigo_ccd_simulator")

file_written = False

_pyindigo.set_shot_processing_callback(save_bytes_to_file)

_pyindigo.take_shot_with_exposure(0.1)

while file_written is False:
    time.sleep(0.01)

print('file written!')

_pyindigo.cleanup_ccd_client()
