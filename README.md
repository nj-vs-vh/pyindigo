# pyindigo — Python interface for INDIGO

[INDIGO](https://github.com/indigo-astronomy/indigo) is a framework for multiplatform and distributed astronomy software development. `pyindigo` is a Python package that lets Python interpreter play the role of Indigo client, that is to control Indigo-compatible devices by exchanging messages over Indigo software bus. To learn about Indigo architecture and basic concepts please refer to [documentation](https://github.com/indigo-astronomy/indigo/tree/master/indigo_docs).

## Contributing

`pyindigo` is in Alpha state, any contribution and/or testing is very welcome! Use Github Issues to report a bug or request a feature, fork/pull request to contribute or [email](mailto:gosha.vaiman@gmail.com?subject=pyindigo+development) me directly for any question. Also check out [TODO](#todo) section.

### Major current limitations

* only one driver at a time is available
* no remote drivers are yet supported
* only on Linux


## Installation

Current installation only works on Linux, and tested specifically on Ubuntu. Installation for other systems is TBD.

1. Prerequisite for this package is Indigo itself. Folow [building instructions](https://github.com/indigo-astronomy/indigo#how-to-build-indigo) for your system, make sure to use `make install` option instead of `make build` to make Indigo available system-wide.

2. Clone this repository

```bash
git clone https://github.com/nj-vs-vh/pyindigo.git
cd pyindigo
```

3. Install `pyindigo_client`. This will copy client's shared library to other indigo shared libraries (`/build/lib`) and set `LD_LIBRARY_PATH` variable to include Indigo libraries.

```bash
cd src/pyindigo_client
make install
```

4. Finally, install the Python package. To let Python link with `pyindigo_client` shared lib, also set `LD_LIBRARY_PATH` to include stadard `/usr/local/lib` location (for repeatable use this may be safely done in .bashrc, or in virtual environment activation script).

```bash
cd ../..
python3 setup.py install
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:"/usr/local/lib"
```

5. Run the example to get started!

```bash
python examples/basic_usage.py
python examples/models_usage.py
```

## Usage

#### Project structure

- `pyindigo_client` is not part of the Python package, but Indigo client shared library written in C. It is dynamically linked with Python C extension module and passes Indigo messages to your Python code. Otherwise it should be treated as any other Indigo client (see [client development basics](https://github.com/indigo-astronomy/indigo/blob/master/indigo_docs/CLIENT_DEVELOPMENT_BASICS.md), and [client examples](https://github.com/indigo-astronomy/indigo/tree/master/indigo_examples) by Indigo).

- `pyindigo.core` package provides direct interface to Indigo functionality. It may be idiomatically imported as `import pyindigo.core as indigo`
  - `pyindigo.core.core_ext` is an extension module writen in C, directly linked to `indigo_bus` and `pyindigo_client` shared libraries. It should not be imported in user-level code.
  - `pyindigo.core.properties` package provides Python classes modelling [Indigo properties](#properties)
  - `pyindigo.core.dispatching_callback` module provides mechanism to set [callback](#listening-for-property-definitionupdatedeletion) that will be invoked on property definition/update/deletion.
  - `pyindigo.core.enums` module provides Python Enum classes modelling enumerations used in Indigo (log level, driver action, etc)
- `pyindigo.enums` module exposes Indigo-related Enum classes for convenience
- `pyindigo.models` — object-oriented wrappers around Indigo functions for more idiomatic and convinient usage
  - `pyindigo.models.client` — "god-object" in the form of Python module, represents the whole Indigo client, keeps track of attached drivers and devices defined by them; also takes care of setup/cleanup
  - `pyindigo.models.driver` — defines class for Indigo driver, currently handles only attachment/detachment, but in future will be used to distinguish between local and remote drivers
  - `pyindigo.models.device` — defines class for Indigo device. It is not instantiated by user, but by callback, when Indigo defines the device. Allows for properties and callbacks, directly linked to specific device.


### Properties

Indigo [**properties**](https://github.com/indigo-astronomy/indigo/blob/master/indigo_docs/PROPERTY_MANIPULATION.md) are essentially messages exchanged between driver and client via Indigo bus. Each property contain several **items** with predefined type: text, number, switch, light (property state) or BLOB. Property also has attributes: name, name of the device that has sent it, state, etc.

Properties are modelled with Python classes in [`pyindigo.core.properties.properties`](https://github.com/nj-vs-vh/pyindigo/blob/main/src/pyindigo/core/properties/properties.py) module. Abstract base class `IndigoProperty` contain common functionality and concrete subclasses represent defferent property types. To construct property one would instantiate appropriate `IndigoProperty` subclass with its attributes and then populate it with items one by one using `add_item` method. For `SwitchVectorProperty` `add_rule` method is used to set switch rule.

```python
some_prop = NumberVectorProperty(device='My Indigo device', name='EXAMPLE')
some_prop.add_item('ITEM1', 0)
some_prop.add_item('ITEM2', 1)
some_prop.add_item('ITEM3', 2)
```

Each property class has corresponding Python class for its items, defined in [`pyindigo.core.properties.items`](https://github.com/nj-vs-vh/pyindigo/blob/main/src/pyindigo/core/properties/items.py). They contain all key attributes from native indigo items, except for some GUI-related stuff. Indigo item values' C data types are mapped to Python data types. Particularly, BLOB item contents is converted to `bytes` object. In case of BLOB containing .fits image corresponding `bytes` object is ready to be turned into `astropy.HDUList` with [`from_string`](https://docs.astropy.org/en/stable/io/fits/api/hdulists.html#astropy.io.fits.HDUList.fromstring) method. URL-based BLOBs from remote devices are not yet supported.

Rule, state, and permission property attributes are stored as enumerations in C code, and corresponding Python Enums are defined in [`pyindigo.core.properties.attribute_enums`](https://github.com/nj-vs-vh/pyindigo/blob/main/src/pyindigo/core/properties/attribute_enums.py).

#### Property schemas

Properties can be instantiated from Python code directly, but it requires copy-pasting property and item names, as `add_item` and `add_rule` methods are intended to be called from C extension code, not high-level Python code. To create properties conviniently and idiomatically, `PropertySchema` objects can be used. These are helper objects defined in [`pyindigo.core.properties.schemas`](https://github.com/nj-vs-vh/pyindigo/blob/main/src/pyindigo/core/properties/schemas.py), that store information from [property tables](https://github.com/indigo-astronomy/indigo/blob/master/indigo_docs/PROPERTIES.md) in a convenient, ready-to-use way. Example:

```python
# namespace classes
from pyindigo.core.properties import CommonProperties, CCDSpecificProperties

prop = CommonProperties.CONNECTION.implement('CCD Imager Simulator', CONNECTED=True)
prop = CCDSpecificProperties.CCD_EXPOSURE.implement('CCD Imager Simulator', EXPOSURE=3)
```

Here `CommonProperties`, `CCDSpecificProperties` are namespace classes corresponding to different property tables, `PropertyNamespace.PROP` is a `PropertySchema`, and with its `implement` method `IndigoProperty` instance is created with specified device and items from keyword args. This way of property instantiation prevents typos in property or item names, and results in more readable code.

Only `CommonProperties` and `CCDSpecificProperties` namespaces are available by now, others are WIP.
v
#### Property setting

To send updated or newly created property to driver, `IndigoProperty.set()` method is used. It wraps C extension function that converts Python object fields to native C data types and calls appropriate Indigo function (i.e. `indigo_change_text_property`). Using property from the previous example, to change CCD device's `CCD_EXPOSURE` property (i.e. request shot exposure of 3 seconds), one would write:

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

## TODO:
- testing with real devices
- testing (unit tests on modules, integration with CCD Imager Simulator)
- multidriver mode — C extension upgrade
- working with remote devices — should be easy, but I haven
- PPA publishing
- OOP bus-driver-device modelling
- helper func for 'ensuring property set' — one-time confirmation callback and 'blocking await' with `while True` until callback returns
- property schemas for the rest of the properties (parse automatically?)
- `.pyi` file for core_ext module

### Open questions:
- Current installation process assumes that Indigo is installed i.e. all files are copied to `/usr/local/...`. This is not easily portable, and requires modifying system directories with sudo. Is there a better way? Some kind of portable install with manually set environment variables to link everything together (Python, Pyindigo client, Indigo lib, Indigo drivers)?
- `enable_blob_mode` — how to use it and do I need to worry about it?
- Agent devices — do they require any extra handling by this client, or this will be entirely on end-users?
- Config property and file — how does it work? When I worked with ZWO camera, it refused to connect unless I manually created file and copied contents from elsewhere? Does this property require any extra care or this behaviour is device-specific?
- What license should I use for distribution?
