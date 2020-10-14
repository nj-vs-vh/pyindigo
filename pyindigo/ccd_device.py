import _pyindigo
from astropy.io.fits import HDUList

import time
import datetime
from pathlib import Path


devices_and_drivers = {
    "indigo_ccd_asi": "ZWO ASI120MC-S #0",
    "indigo_ccd_simulator": "CCD Imager Simulator",
}


driver = list(devices_and_drivers.keys())[0]
device = devices_and_drivers[driver]


images_path = Path('../images')


def save_bytes_to_file(b: bytes = None) -> None:
    try:
        global file_written
        hdul = HDUList.fromstring(b)
        hdul.writeto(images_path / f'IMG_{datetime.datetime.now().strftime("%Y_%m_%d_%X")}.fits')
    except Exception as e:
        print(f'error occured in callback: {e}')
    file_written = True


_pyindigo.set_device_name(device)

_pyindigo.setup_ccd_client(driver)

print('waiting for setup...')

time.sleep(5)

_pyindigo.set_shot_processing_callback(save_bytes_to_file)
_pyindigo.set_gain(20.0)

_pyindigo.take_shot_with_exposure(0.01)

print('exposing...')

file_written = False
while file_written is False:
    time.sleep(0.01)

print('callback executed!')

_pyindigo.cleanup_ccd_client()
