import _pyindigo
from client import indigo_client
from device import IndigoDevice


class IndigoDriver:

    # reference to 'parent' client
    client = indigo_client

    def __init__(self, driver_lib_name):
        self.devices = []
        _pyindigo.attach_indigo_driver(
            driver_lib_name,
            self.device_defined_callback,
            self.device_connected_callback,
            self.device_disconnected_callback
        )

    def device_defined_callback(self, device_name):
        print(f'{device_name} is defined!')
        # try:
        #     self.devices.append(IndigoDevice(device_name))
        # except Exception as e:
        #     print(e)

    def device_connected_callback(self, device_name):
        print(f'{device_name} is connected!')
        # print(device_name)
        # try:
        #     device = self.find_device_by_name(device_name)
        #     device.connected = True
        # except Exception as e:
        #     print(e)

    def device_disconnected_callback(self, device_name):
        print(f'{device_name} is disconnected!')
        # try:
        #     device = self.find_device_by_name(device_name)
        #     device.connected = False
        # except Exception as e:
        #     print(e)

    def find_device_by_name(self, device_name: str) -> IndigoDevice:
        print(device_name)
        for device in self.devices:
            if device.name == device_name:
                return device
        else:
            raise KeyError(f"No device named '{device_name}' found")


if __name__ == "__main__":
    import time
    driver = IndigoDriver('indigo_ccd_simulator')
    time.sleep(1)
    print(driver.devices)
