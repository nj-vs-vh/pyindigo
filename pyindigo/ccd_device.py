import time

import _pyindigo


def save_bytes_to_file(b: bytes = None) -> None:
    global file_written
    # with open('temp.fits', 'wb') as f:
    #     f.write(b)
    file_written = True


for i in range(50):

    # print(_pyindigo.version())

    _pyindigo.set_device_name("CCD Imager Simulator")
    _pyindigo.get_current_device_name()

    _pyindigo.setup_ccd_client("indigo_ccd_simulator")

    file_written = False

    _pyindigo.set_shot_processing_callback(save_bytes_to_file)

    _pyindigo.take_shot_with_exposure(0.1)

    while file_written is False:
        time.sleep(0.01)

    print('file written!')

    time.sleep(0.1)

    _pyindigo.cleanup_ccd_client()

    time.sleep(0.1)
