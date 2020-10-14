# import _pyindigo


class IndigoDevice:

    def __init__(self, device_name: str):
        self.name = device_name
        self.connected = False
