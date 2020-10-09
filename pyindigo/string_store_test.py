import _pyindigo

string_tuple = ('one', 'two')

for i in range(1):
    _pyindigo.set_device_name_and_driver(*string_tuple)
    recovered = _pyindigo.get_current_device_name_and_driver()
    if recovered != string_tuple:
        raise RuntimeError("AAAA")
