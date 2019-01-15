"""
Support for WeBeHome binary sensor.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/binary_sensor.webehome/
"""

import logging
from typing import Optional

from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from custom_components.webehome import (DATA_WEBEHOME, SIGNAL_UPDATE_DEVICES,
                                        WeBeHomeEntity)
from pybehome import Device
from pybehome.constants import DOOR_WINDOW_OPEN, MOTION_DETECTED

DEPENDENCIES = ['webehome']

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the WeBeHome binary sensor."""

    session = hass.data[DATA_WEBEHOME]

    devices = []
    session.update_devices()
    for device in session.get_devices():
        if device.display_type not in [300, 310]:
            continue
        devices.append(WeBeHomeBinarySensorDevice(session, device))

    async_add_entities(devices)

    return True


class WeBeHomeBinarySensorDevice(WeBeHomeEntity, BinarySensorDevice):
    """Representation of a WeBeHome binary sensor."""

    def __init__(self, session, device: Device):
        """Initialize a binary sensor for WeBeHome device."""
        super().__init__(session)
        self._device = device

    async def async_added_to_hass(self):
        """Register update dispatcher."""
        @callback
        def async_device_update():
            """Update callback."""
            self.async_schedule_update_ha_state(True)

        async_dispatcher_connect(
            self.hass, SIGNAL_UPDATE_DEVICES, async_device_update)

    async def async_update(self):
        """Fetch new state data for the sensor."""
        self._device = self._session.get_device(self._device.device_id)

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return "webehome_{}".format(self._device.device_id)

    @property
    def name(self) -> Optional[str]:
        """Return name of device."""
        return "{}_{}".format(self._device.type.lower(), self._device.name)

    @property
    def state_attributes(self):
        """Return the state attributes."""
        return {
            "friendly_name": self._device.name,
            "type": self._device.type,
            "display_type": self._device.display_type,
            "battery_level": self._device.battery_level,
            "operation_status": self._device.operation_status,
            "last_event_time": self._device.last_event_time,
            "last_event_data": self._device.last_event_data,
            "lost_connection": self._device.lost_connection
        }

    @property
    def device_class(self):
        """Return the class of this binary sensor."""
        if self._device.display_type == 300:
            return 'door'
        elif self._device.display_type == 310:
            return 'motion'
        elif self._device.display_type == 500:
            return 'smoke'
        else:
            return None

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        if not self._device.lost_connection:
            return True
        return False

    @property
    def is_on(self) -> bool:
        """Return the state of the binary sensor."""
        if self._device.display_type == 300:
            return self._device.operation_status == DOOR_WINDOW_OPEN
        elif self._device.display_type == 310:
            return self._device.operation_status == MOTION_DETECTED
