# pyindigo — Python interface for [INDIGO](https://github.com/indigo-astronomy/indigo) framework

## TODO:
- proper readme :)
- testing (unit tests on modules, integration with CCD Imager Simulator)
- test coroutine callbacks
- namespacing - more convenient imports
- ensuring property set (one-time callback confirmation and blocking await before callback returns) - maybe a separate method?
- OOP bus-driver-device modelling (see `old` dir)
- parse rest of the properties to schemas
- multidriver mode - C extension upgrade

## Open questions:
- enable_blob_mode - how to use it and do I need to worry about it
- working with remote devices - should be easy, but still (see indigo_cffi package)
- config property - how does it work? why ZWO camera wasn't able to start until I created config file manually
- 
