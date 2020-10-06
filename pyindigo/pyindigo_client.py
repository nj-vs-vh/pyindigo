# debugging
# export PYTHONPATH="/home/njvh/Documents/Science/sphere/camera-server/pyindigo/bin/shared"

import importlib.util
spec = importlib.util.spec_from_file_location(
    "_pyindigo",
    "/home/njvh/Documents/Science/sphere/camera-server/pyindigo/build/lib.linux-x86_64-3.8/"
    + "_pyindigo.cpython-38-x86_64-linux-gnu.so",
)
_pyindigo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_pyindigo)

print(_pyindigo.version())
