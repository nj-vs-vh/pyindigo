import _pyindigo

print(_pyindigo.version())

_pyindigo.set_ccd_driver_and_device("CCD Imager Simulator", "indigo_ccd_simulator")

_pyindigo.setup_ccd_client()


def save_bytes_to_file(b: bytes) -> None:
    print('test')
    with open('temp.fits', 'wb') as f:
        f.write(b)
    _pyindigo.cleanup_ccd_client()
    exit()


_pyindigo.take_shot_with_exposure(5.0, save_bytes_to_file)

while True:
    pass
