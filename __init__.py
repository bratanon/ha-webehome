"""
Support for WeBeHome components.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/webehome/
"""

import logging
from datetime import timedelta

import voluptuous as vol
from homeassistant.const import (CONF_PASSWORD, CONF_USERNAME,
                                 EVENT_HOMEASSISTANT_STOP)
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import discovery
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.util.dt import utcnow

REQUIREMENTS = ['https://github.com/bratanon/pybehome/archive/1.0.1.zip'
                '#pybehome==1.0.1']

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'webehome'
DATA_WEBEHOME = 'data_webehome'

DEVICE_SCAN_INTERVAL = timedelta(seconds=5)

SIGNAL_UPDATE_DEVICES = 'webehome_device_update'
SIGNAL_UPDATE_LOCATION = 'webehome_location_update'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    })
}, extra=vol.ALLOW_EXTRA)

WEBEHOME_PLATFORMS = [
    'alarm_control_panel', 'binary_sensor'
]


async def async_setup(hass, config):
    """Setup the WeBeHome component."""
    if DOMAIN not in config:
        return True

    from pybehome import PyBeHome

    conf = config[DOMAIN]
    username = conf.get(CONF_USERNAME)
    password = conf.get(CONF_PASSWORD)

    hass.data[DATA_WEBEHOME] = PyBeHome(username, password)

    result = await hass.async_add_executor_job(hass.data[DATA_WEBEHOME].login)
    if not result:
        _LOGGER.exception("Unable to connect to WeBeHome OPEN API")
        return False

    for platform in WEBEHOME_PLATFORMS:
        discovery.load_platform(hass, platform, DOMAIN, {}, config)

    async def async_update_device_data(now):
        result = await hass.async_add_executor_job(hass.data[DATA_WEBEHOME].update_devices)
        async_dispatcher_send(hass, SIGNAL_UPDATE_DEVICES)

        async_track_point_in_utc_time(
            hass, async_update_device_data, utcnow() + DEVICE_SCAN_INTERVAL)

    async def async_update_location_data(now):
        result = await hass.async_add_executor_job(hass.data[DATA_WEBEHOME].update_location)
        async_dispatcher_send(hass, SIGNAL_UPDATE_LOCATION)

        async_track_point_in_utc_time(
            hass, async_update_location_data, utcnow() + DEVICE_SCAN_INTERVAL)

    await async_update_device_data(None)
    await async_update_location_data(None)

    @callback
    async def logout(event):
        """Logout of WeBeHome OPEN API."""
        result = await hass.async_add_executor_job(hass.data[DATA_WEBEHOME].token_destroy)

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, logout)

    return True


class WeBeHomeEntity(Entity):
    def __init__(self, session):
        """Initialize a binary sensor for WeBeHome device."""
        self._session = session

    @property
    def should_poll(self):
        """No polling needed."""
        return False
