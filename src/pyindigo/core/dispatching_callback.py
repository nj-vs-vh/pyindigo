"""Dispatching callback is a single Python callable invoked from C code to process all properties"""


from .properties.properties import IndigoProperty
from .enums import IndigoDriverAction


def dispatching_callback(action_string: str, property: IndigoProperty):
    action = IndigoDriverAction(action_string)
    print(action)
    # TODO: actual dispatching...
    #       @register decorator
    #       filtering based on property device, name, type, etc
    #       option for one-shot callback
    #       loop option for coroutine callbacks (asyncio.run_coroutine_threadsafe)
