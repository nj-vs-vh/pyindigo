"""Property schemas (name, type, possible item names, rule for switch properties)
for easier property construction from Python code. Analagous to indigo_names.h

See full info at https://github.com/indigo-astronomy/indigo/blob/master/indigo_docs/PROPERTIES.md

Schemas cover only writeable properties

TODO: interface-specific properties beyond CCDs (DSLR, focuser, wheel, mount, etc)
"""

from dataclasses import dataclass
from typing import Type, List, Optional, Any

from .properties import (
    IndigoProperty,
    TextVectorProperty,
    NumberVectorProperty,
    SwitchVectorProperty,
    BlobVectorProperty,
)
from .attribute_enums import IndigoSwitchRule


@dataclass
class PropertySchema:
    property_name: str
    property_class: Type[IndigoProperty]
    allowed_item_names: List[str]  # empty list means any item name is accepted
    rule: Optional[IndigoSwitchRule] = None

    def implement(self, device: str, single_item_value: Optional[Any] = None, **items_kwargs) -> IndigoProperty:
        """Use schema to create property ready for setting

        Property items must be specified with keyword arguments ITEM_NAME='item_value' or,
        if there's only one item in the property, with single value"""
        prop = self.property_class(device=device, name=self.property_name)
        if self.rule and self.property_class is SwitchVectorProperty:
            prop.add_rule(self.rule)
        if single_item_value is not None:
            if items_kwargs:
                raise ValueError("Single item value and items keyword args cannot be used together!")
            if len(self.allowed_item_names) > 1:
                raise ValueError(
                    "Single item value argument can only be used for single-item properties, "
                    + f"but {self.property_name} has {len(self.allowed_item_names)} of them"
                )
            prop.add_item(self.allowed_item_names[0], single_item_value)
        else:
            if not items_kwargs:
                raise ValueError("At least one item must be specified!")
            for item_name, item_value in items_kwargs.items():
                if item_name in self.allowed_item_names or len(self.allowed_item_names) == 0:
                    prop.add_item(item_name, item_value)
                else:
                    raise KeyError(f"Property {self.property_name} doesn't have {item_name} item!")
        return prop


class IndigoPropertiesNamespace:
    """Base class for all namespaces."""
    def __new__(cls):
        raise RuntimeError(f"{cls.__name__} is a namespace class, it cannot be instantiated!")


class CommonProperties(IndigoPropertiesNamespace):
    """https://github.com/indigo-astronomy/indigo/blob/master/indigo_docs/PROPERTIES.md#common-properties"""

    CONNECTION = PropertySchema(
        'CONNECTION', SwitchVectorProperty, ['CONNECTED', 'DISCONNECTED'], rule=IndigoSwitchRule.EXACTLY_ONE
    )

    INFO = PropertySchema(
        'INFO', TextVectorProperty, [
            'DEVICE_NAME',
            'DEVICE_VERSION',
            'DEVICE_INTERFACE',
            'FRAMEWORK_NAME',
            'FRAMEWORK_VERSION',
            'DEVICE_MODEL',
            'DEVICE_FIRMWARE_REVISION',
            'DEVICE_HARDWARE_REVISION',
            'DEVICE_SERIAL_NUMBER'
        ],
    )

    SIMULATION = PropertySchema(
        'SIMULATION', SwitchVectorProperty, ['ENABLED', 'DISABLED'], rule=IndigoSwitchRule.EXACTLY_ONE
    )

    CONFIG = PropertySchema(
        'CONFIG', SwitchVectorProperty, ['LOAD', 'SAVE', 'REMOVE'], rule=IndigoSwitchRule.AT_MOST_ONE
    )

    # Number of profiles is device-specific, so allow as many as 100 :)
    PROFILE = PropertySchema(
        'PROFILE', SwitchVectorProperty, [f'PROFILE_{i}' for i in range(100)], rule=IndigoSwitchRule.EXACTLY_ONE
    )

    # Either device path like "/dev/tty0" or URL like "lx200://host:port".
    DEVICE_PORT = PropertySchema('DEVICE_PORT', TextVectorProperty, ['PORT'])

    # When selected, it is copied to DEVICE_PORT property.
    DEVICE_PORTS = PropertySchema('DEVICE_PORTS', SwitchVectorProperty, [], rule=IndigoSwitchRule.EXACTLY_ONE)

    # Serial port configuration in a string like this: 9600-8N1
    DEVICE_BAUDRATE = PropertySchema('DEVICE_BAUDRATE', TextVectorProperty, ['BAUDRATE'])

    GEOGRAPHIC_COORDINATES = PropertySchema(
        'GEOGRAPHIC_COORDINATES', NumberVectorProperty, ['LATITUDE', 'LONGITUDE', 'ELEVATION', 'ACCURACY']
    )

    # Depending on hardware this property can be read-only!
    UTC_TIME = PropertySchema('UTC_TIME', NumberVectorProperty, ['TIME', 'OFFSET'])


class CCDSpecificProperties(IndigoPropertiesNamespace):
    """"https://github.com/indigo-astronomy/indigo/blob/master/indigo_docs/PROPERTIES.md#ccd-specific-properties"""

    # All in centimeters
    CCD_LENS = PropertySchema('CCD_LENS', NumberVectorProperty, ['APERTURE', 'FOCAL_LENGTH'])

    CCD_UPLOAD_MODE = PropertySchema(
        'CCD_UPLOAD_MODE', SwitchVectorProperty, ['CLIENT', 'LOCAL', 'BOTH'], rule=IndigoSwitchRule.EXACTLY_ONE
    )

    # XXX in DIR is replaced by sequence
    CCD_LOCAL_MODE = PropertySchema('CCD_LOCAL_MODE', TextVectorProperty, ['DIR', 'PREFIX'])

    CCD_EXPOSURE = PropertySchema('CCD_EXPOSURE', NumberVectorProperty, ['EXPOSURE'])

    # The same as CCD_EXPOSURE, but will upload COUNT images. Use COUNT -1 for endless loop.
    CCD_STREAMING = PropertySchema('CCD_STREAMING', NumberVectorProperty, ['EXPOSURE', 'COUNT'])

    CCD_ABORT_EXPOSURE = PropertySchema(
        'CCD_ABORT_EXPOSURE', SwitchVectorProperty, ['ABORT_EXPOSURE'], rule=IndigoSwitchRule.EXACTLY_ONE
    )

    # If BITS_PER_PIXEL can't be changed, set min and max to the same value.
    CCD_FRAME = PropertySchema('CCD_FRAME', NumberVectorProperty, ['LEFT', 'TOP', 'WIDTH', 'HEIGHT', 'BITS_PER_PIXEL'])

    # CCD_MODE is prefered way how to set binning.
    CCD_BIN = PropertySchema('CCD_BIN', NumberVectorProperty, ['HORIZONTAL', 'VERTICAL'])

    # Item names are device-specific and can be anything
    CCD_MODE = PropertySchema('CCD_MODE', SwitchVectorProperty, [], rule=IndigoSwitchRule.EXACTLY_ONE)

    CCD_READ_MODE = PropertySchema(
        'CCD_READ_MODE', SwitchVectorProperty, ['HIGH_SPEED', 'LOW_NOISE'], rule=IndigoSwitchRule.EXACTLY_ONE
    )

    CCD_GAIN = PropertySchema('CCD_GAIN', NumberVectorProperty, 'GAIN')

    CCD_OFFSET = PropertySchema('CCD_OFFSET', NumberVectorProperty, 'OFFSET')

    CCD_GAMMA = PropertySchema('CCD_GAMMA', NumberVectorProperty, 'GAMMA')

    CCD_FRAME_TYPE = PropertySchema(
        'CCD_FRAME_TYPE', SwitchVectorProperty, ['LIGHT', 'BIAS', 'DARK', 'FLAT'], rule=IndigoSwitchRule.EXACTLY_ONE
    )

    CCD_IMAGE_FORMAT = PropertySchema(
        'CCD_IMAGE_FORMAT', SwitchVectorProperty,
        [
            'RAW', 'FITS', 'XISF', 'JPEG',
            'JPEG_AVI',  # JPEG for capture, AVI for streaming
            'RAW_SER'  # RAW for capture, SER for streaming
        ],
        rule=IndigoSwitchRule.EXACTLY_ONE
    )

    CCD_IMAGE_FILE = PropertySchema('CCD_IMAGE_FILE', TextVectorProperty, ['FILE'])

    CCD_IMAGE = PropertySchema('CCD_IMAGE', BlobVectorProperty, ['IMAGE'])

    # Depending on hardware this may be a read-only property
    CCD_TEMPERATURE = PropertySchema('CCD_TEMPERATURE', NumberVectorProperty, ['TEMPERATURE'])

    CCD_COOLER = PropertySchema('CCD_COOLER', SwitchVectorProperty, ['ON', 'OFF'], rule=IndigoSwitchRule.EXACTLY_ONE)

    # Depending on hardware this may be a read-only property
    CCD_COOLER_POWER = PropertySchema('CCD_COOLER_POWER', NumberVectorProperty, ['POWER'])

    # String in form "name = value", "name = 'value'" or "comment text"
    CCD_FITS_HEADERS = PropertySchema('CCD_FITS_HEADERS', TextVectorProperty, [f'HEADER_{i}' for i in range(100)])

    # Send JPEG preview to client
    CCD_PREVIEW = PropertySchema(
        'CCD_PREVIEW', SwitchVectorProperty, ['ENABLED', 'DISABLED'], rule=IndigoSwitchRule.EXACTLY_ONE
    )
