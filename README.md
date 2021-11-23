[![License](http://img.shields.io/badge/INDIGO-license-red.svg)](https://github.com/indigo-astronomy/indigo/blob/master/LICENSE.md)

# pyindigo — Python interface for INDIGO

[INDIGO](https://github.com/indigo-astronomy/indigo) is a framework for multiplatform and distributed astronomy software development. `pyindigo` is a Python package that lets Python interpreter play the role of Indigo client, that is to control Indigo-compatible devices by exchanging messages over Indigo software bus. To learn about Indigo architecture and basic concepts please refer to [documentation](https://github.com/indigo-astronomy/indigo/tree/master/indigo_docs).

## Contributing

`pyindigo` is in Alpha state, any contribution and/or testing is very welcome! Use Github Issues to report a bug or request a feature, fork/pull request to contribute or [email](mailto:gosha.vaiman@gmail.com?subject=pyindigo+development) me directly for any question. Also check out [TODO](#todo) section.

### Major current limitations

* only one driver at a time is available
* no remote drivers are yet supported
* tested only on Linux


## Installation

1. Prerequisite for this package is Indigo itself. Follow [building instructions](https://github.com/indigo-astronomy/indigo#how-to-build-indigo) for your system, make sure to use `make install` option instead of `make build` to make Indigo available system-wide.

4. Clone this repository

    ```bash
    git clone https://github.com/nj-vs-vh/pyindigo.git
    cd pyindigo
    ```

5. Install `pyindigo_client`. This will copy client's shared library to other indigo shared libraries (`/usr/local/lib`).

    ```bash
    cd src/pyindigo_client
    make install
    ```

6. Finally, install the Python package. To let Python link with `pyindigo_client` shared lib in runtime, make sure that `LD_LIBRARY_PATH` includes `/usr/local/lib` location.

    ```bash
    cd ../..
    python3 setup.py install
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:"/usr/local/lib"
    ```

7. Run an example to get started!

```bash
python examples/basic_usage.py
python examples/models_usage.py
```

### Uninstall

To uninstall `pyindigo`, you can use following commands form pyindigo directory

```bash
pip uninstall pyindigo -y
sudo rm -rf ./build ./dist ./src/pyindigo.egg-info
cd src/pyindigo_client
make clean
```

If you have tweaked the source code and want to quickly test it, you can use `dev_reinstall.sh` script.

## Usage

#### Project structure

- `pyindigo_client` is an Indigo client shared library written in C. It is dynamically linked with Python C extension module and passes messages between Indigo and Python interpreter. Otherwise it should be treated as any other Indigo client (see [client development basics](https://github.com/indigo-astronomy/indigo/blob/master/indigo_docs/CLIENT_DEVELOPMENT_BASICS.md), and [client examples](https://github.com/indigo-astronomy/indigo/tree/master/indigo_examples) by Indigo).

- `pyindigo.core` package provides direct interface to Indigo functionality. It may be idiomatically imported as `import pyindigo.core as indigo`
  - `pyindigo.core.core_ext` is an extension module writen in C, directly linked to `indigo_bus` and `pyindigo_client` shared libraries. It should not be imported in user-level code.
  - `pyindigo.core.properties` package provides Python classes modelling [Indigo properties](#properties)
  - `pyindigo.core.dispatching_callback` module provides mechanism to set [callbacks](#listening-for-property-definitionupdatedeletion) which will be invoked on property definition/update/deletion.
  - `pyindigo.core.enums` module provides Python Enum classes modelling enumerations used in Indigo (log level, driver action, etc)
- `pyindigo.models` provides object-oriented wrappers around Indigo functions for more idiomatic and convinient usage
  - `pyindigo.models.client` is a "god-object" in the form of Python module, represents the whole Indigo client, keeps track of attached drivers and devices defined by them; also takes care of setup/cleanup
  - `pyindigo.models.driver` defines class for Indigo driver that handles only attachment/detachment
  - `pyindigo.models.device` defines class for Indigo device. It is not instantiated by user, but by callback, when Indigo defines the device. Allows for properties and callbacks, directly linked to specific device.


### Properties

Indigo [**properties**](https://github.com/indigo-astronomy/indigo/blob/master/indigo_docs/PROPERTY_MANIPULATION.md) are essentially messages exchanged between driver and client via Indigo bus. Each property contain several **items** with predefined type: text, number, switch, light (property state) or BLOB. Property also has attributes: name, name of the device that has sent it, state, etc.

Properties are modelled with Python classes in [`pyindigo.core.properties.properties`](https://github.com/nj-vs-vh/pyindigo/blob/main/src/pyindigo/core/properties/properties.py) module. Abstract base class `IndigoProperty` contain common functionality and concrete subclasses represent defferent property types. To construct property one would instantiate appropriate `IndigoProperty` subclass with its attributes and then populate it with items one by one using `add_item` method. For `SwitchVectorProperty` `add_rule` method is used to set switch rule.

```python
some_prop = NumberVectorProperty(device='My Indigo device', name='EXAMPLE')
some_prop.add_item('ITEM1', 0)
some_prop.add_item('ITEM2', 1)
some_prop.add_item('ITEM3', 2)
```

Each property class has corresponding Python class for its items, defined in [`pyindigo.core.properties.items`](https://github.com/nj-vs-vh/pyindigo/blob/main/src/pyindigo/core/properties/items.py). They contain all key attributes from native indigo items, except for some GUI-related stuff. Indigo item values' C data types are mapped to Python data types. Particularly, BLOB item contents are converted to `bytes` object. In case of BLOB containing .fits image corresponding `bytes` object is ready to be turned into `astropy.HDUList` with [`from_string`](https://docs.astropy.org/en/stable/io/fits/api/hdulists.html#astropy.io.fits.HDUList.fromstring) method. URL-based BLOBs from remote devices are not yet supported.

Rule, state, and permission property attributes are stored as enumerations in C code, and corresponding Python Enums are defined in [`pyindigo.core.properties.attribute_enums`](https://github.com/nj-vs-vh/pyindigo/blob/main/src/pyindigo/core/properties/attribute_enums.py).

#### Property schemas

Properties can be instantiated from Python code directly, but it requires copy-pasting property and item names. To create properties easily, `PropertySchema` objects can be used. These are helper objects defined in [`pyindigo.core.properties.schemas`](https://github.com/nj-vs-vh/pyindigo/blob/main/src/pyindigo/core/properties/schemas.py), that store information from [property tables](https://github.com/indigo-astronomy/indigo/blob/master/indigo_docs/PROPERTIES.md) in a convenient, ready-to-use way. Example:

```python
from pyindigo.core.properties import CommonProperties, CCDSpecificProperties

# the most common way: keyword arguments, simple and intuitive
prop = CommonProperties.CONNECTION.implement('CCD Imager Simulator', CONNECTED=True)
prop = CCDSpecificProperties.CCD_EXPOSURE.implement('CCD Imager Simulator', EXPOSURE=3)
# or like that, when a property has a single item and it's name is obvious
prop = CCDSpecificProperties.CCD_EXPOSURE.implement('CCD Imager Simulator', 3)
# or like that, when item name cannot fit in a python keyword
from pyindigo.core.properties import UserDefinedItem
prop = CCDSpecificProperties.CCD_EXPOSURE.implement(
    'CCD Imager Simulator',
    UserDefinedItem("Some device-specific item", True),
    UserDefinedItem("Some other device-specific item", False),
)
```

Here `CommonProperties`, `CCDSpecificProperties` are "namespace" classes corresponding to different property tables, They contain various schemas, and for each you can use `implement` method to create an actual `IndigoProperty` instance with specified target device and items (from keyword args). Property schemas are smart enough to raise an exception if you use inappropriate item names. This way of property instantiation results in readable code without magic string constants.

Only `CommonProperties` and `CCDSpecificProperties` schema classes are available for now.

#### Property setting

To send updated or newly created property to driver, `IndigoProperty.set()` method is used. It wraps C extension function that converts Python object fields to native C data types and calls an appropriate Indigo function (i.e. `indigo_change_text_property`). Using property from the previous example, to change CCD device's `CCD_EXPOSURE` property (i.e. request shot exposure of 3 seconds), one would write:

```python
prop = CCDSpecificProperties.CCD_EXPOSURE.implement('CCD Imager Simulator', EXPOSURE=3)
prop.set()
```

### Listening for property definition/update/deletion

"Dispatching callback" is a single Python function that is sent to C extension module on core initialization and is invoked on any driver action. `pyindigo` provides `indigo_callback` decorator to inject your functions or coroutines to be executed on all or some driver actions and properties. The basic usage is

```python
@indigo_callback
def my_callback(action: IndigoDriverAction, prop: IndigoProperty):
    print(f"{action}: {prop}")
```

This code will register function in dispatching callback and all messages from drivers will be passed to it. Please note that exceptions in callbacks are silently catched by dispatching callback by default, so you should do your own exception handling.

Dispatching callback can also do some basic filtering for you and invoke your callback only with specific properties and specific driver action.

```python
@indigo_callback(
    accepts={
        'action': IndigoDriverAction.UPDATE,
        'device': 'CCD Imager simulator',
        'name': CommonProperties.CONNECTION.property_name,
        'state': IndigoPropertyState.OK
    },
    run_times=3
)
def my_callback(action: IndigoDriverAction, prop: IndigoProperty):
    some_processing(prop)
```

In this case only first 3 CONNECTION property updates from CCD Imager simulator in OK state will be passed to the callback, then it will be discarded. `accepts` argument is a `dict` with the following keys and expected value types: `action`: `IndigoDriverAction`, `property_class`: `TypeVar[IndigoProperty]`, `device`, `name`, `state`, `perm`, `rule` all expect the same types as corresponding fields of `IndigoProperty` class.

There's also native support for `asyncio` coroutines as callbacks. In this case you **must** pass a `loop` argument to `indigo_callback` decorator, and callback coroutine will be run in this loop with [`asyncio.run_coroutine_threadsafe`](https://docs.python.org/3/library/asyncio-task.html#asyncio.run_coroutine_threadsafe)

```python
@indigo_callback(loop=loop)
async def coroutine_callback(action: IndigoDriverAction, prop: IndigoProperty):
    await some_asynchronous_processing(prop)
```

Finally, when using `indigo_callback` as a decorator, callback is registered at parse time. To control callback registration time precisely at runtime, one would simply use

```python
indigo_callback(my_callback, accepts={'state': IndigoPropertyState.ALERT})
```

### Using device and driver classes

Some actions like connecting to device are common and may be abstracted a little bit. In particular, there's `pyindigo.models` subpackage with optional classes providing such abstractions.

Example usage:

```python
# Indigo thread starts right here at the moment you import anything from models subpackage!
from pyindigo.models.driver import IndigoDriver
import pyindigo.models.client as client

from pyindigo.core.properties import CCDSpecificProperties, BlobVectorProperty
from pyindigo.core.enums import IndigoDriverAction, IndigoPropertyState

# here indigo will attempt to load dynamic driver
driver = IndigoDriver('indigo_ccd_simulator')

# driver is attached on demand and will be detached automatically on exit
# (or can be detached manually driver.detach())
driver.attach()

# client keeps track of all known devices and can find them by name
simulator = client.find_device('CCD Imager Simulator')

# connecting to device -- blocking=True will prevent program for continuing until confirmation from driver is received
simulator.connect(blocking=True)

# shortcut to restrict callback to propetries from particular device
@simulator.callback(
    accepts={...}
)
def some_clbck(action: IndigoDriverAction, prop: BlobVectorProperty):
    pass

# similar to CCDSpecificProperties.CCD_EXPOSURE.implement('CCD Imager Simulator', EXPOSURE=3).set()
# but more expressive
simulator.set_property(CCDSpecificProperties.CCD_EXPOSURE, EXPOSURE=5)
```

### Troubleshooting and logging

Troubleshooting INDIGO app can be painful due to it's asynchronous and multithreading nature. With `pyindigo` you have two options:

1. Native Indigo logs. This sets appropriate flag in C code, logs are channeled to Python output directly from there:

```python
from pyindigo.core import set_indigo_log_level, IndigoLogLevel
set_indigo_log_level(IndigoLogLevel.DEBUG)

# example log:
# 16:15:05.798191 Application: indigo_ccd_simulator: 'CCD Imager Simulator (wheel)' attached
```

2. Logging events on Python side with `pyindigo.logging`. This module wraps standard Python `logging` with additional config option:

```python
import pyindigo.logging as logging
# how you would use standart logging module to log to file:
logging.basicConfig(filename='pyindigo.log', level=logging.DEBUG)

# additional options:
logging.pyindigoConfig(
    log_driver_actions=True,  # log every property on every action coming through dispatching callback (INFO level, False be default)
    log_property_set=True,  # log every property set by Python client (INFO level, False be default)
    log_callback_dispatching=True,  # which property goes to which callback function (INFO level, False be default)
    log_device_connection=True,  # device connection log for pyindigo.models.device (INFO level, False be default)
    log_alert_properties=True,  # like log_driver_actions, but only for alert state (INFO level, False be default)
    log_callback_exceptions=True  # log exceptions in indigo callbacks (WARNING level, True be default)
)
```

## TODO:
- testing with real devices
- testing (unit tests on modules, integration with CCD Imager Simulator)
- multidriver mode — C extension upgrade
- working with remote devices — should be easy
- PPA publishing
- property schemas for the rest of the properties (parse tables automatically?)
- `.pyi` file for core_ext module

### Open questions:
- Current installation process assumes that Indigo is installed i.e. all files are copied to `/usr/local/...`. This is not easily portable, and requires modifying system directories with sudo. Is there a better way? Some kind of portable install with manually set environment variables to link everything together (Python, Pyindigo client, Indigo lib, Indigo drivers)?
- `enable_blob_mode` — how to use it and do I need to worry about it? This seems important for remote operation.
