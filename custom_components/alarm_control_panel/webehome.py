"""
Support for WeBeHome alarm control panel.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/alarm_control_panel.webehome/
"""

import logging

from homeassistant.components.alarm_control_panel import AlarmControlPanel
from homeassistant.const import (STATE_ALARM_ARMED_AWAY,
                                 STATE_ALARM_ARMED_HOME, STATE_ALARM_DISARMED,
                                 STATE_UNKNOWN)
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from custom_components.webehome import (DATA_WEBEHOME, SIGNAL_UPDATE_LOCATION,
                                        WeBeHomeEntity)
from pybehome import Location
from pybehome.constants import (ALARM_ARMED_AWAY, ALARM_ARMED_HOME,
                                ALARM_DISARMED)

DEPENDENCIES = ['webehome']

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Set up a WeBeHome control panel."""
    session = hass.data[DATA_WEBEHOME]

    session.update_location()
    location = session.get_location()
    async_add_entities([WeBeHomeAlarm(session, location)])

    return True


class WeBeHomeAlarm(WeBeHomeEntity, AlarmControlPanel):
    """Representation of a WeBeHome alarm status."""

    def __init__(self, session, location: Location, code=None):
        """Initialize the WeBeHome alarm panel."""
        super().__init__(session)
        self._location = location

    async def async_added_to_hass(self):
        """Register update dispatcher."""
        @callback
        def async_location_update():
            """Update callback."""
            self.async_schedule_update_ha_state(True)

        async_dispatcher_connect(
            self.hass, SIGNAL_UPDATE_LOCATION, async_location_update)

    async def async_update(self):
        """Fetch new state data for the sensor."""
        self._location = self._session.get_location()

    @property
    def name(self):
        """Return name of location."""
        return 'alarm_{}'.format(self._location.base_unit_id)

    @property
    def base_unit_id(self):
        """Return the base_unit_id of the location."""
        return self._location.base_unit_id

    @property
    def changed_by(self):
        """Last change triggered by."""
        return self._location.operation_status_info

    @property
    def operation_status(self):
        """Return the operation_status of the location."""
        return self._location.operation_status

    @property
    def connection_status(self):
        """Return the connection status of the location."""
        online_position = self._location.operation_status[1]
        if online_position == '0':
            return 'Online'

        return 'Offline'

    @property
    def operation_status_info(self):
        """Return the operation_status_info of the location."""
        return self._location.operation_status_info

    @property
    def state(self):
        """Return the state of the location."""
        alarm_state = int(self._location.operation_status[0])

        if alarm_state == ALARM_DISARMED:
            return STATE_ALARM_DISARMED
        if alarm_state == ALARM_ARMED_AWAY:
            return STATE_ALARM_ARMED_AWAY
        if alarm_state == ALARM_ARMED_HOME:
            return STATE_ALARM_ARMED_HOME

        return STATE_UNKNOWN

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        if self.state == STATE_ALARM_DISARMED:
            return 'mdi:shield-outline'
        if self.state == STATE_ALARM_ARMED_AWAY:
            return 'mdi:shield'
        if self.state == STATE_ALARM_ARMED_HOME:
            return 'mdi:shield-half-full'

        return 'mdi:help'

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            'friendly_name': self._location.name,
            'type': 'location',
            'base_unit_id': self._location.base_unit_id,
            'online_status': self.connection_status,
            'operation_status': self._location.operation_status,
            'operation_status_info': self._location.operation_status_info
        }

    def alarm_disarm(self, code=None):
        """Send disarm command."""
        _LOGGER.debug("Set arm state: DISARMED")
        return self._session.set_alarm_state('Disarm')

    def alarm_arm_home(self, code=None):
        """Send arm home command."""
        _LOGGER.debug("Set arm state: ARMED_HOME")
        return self._session.set_alarm_state('ArmHome')

    def alarm_arm_away(self, code=None):
        """Send arm away command."""
        _LOGGER.debug("Set arm state: ARMED_AWAY")
        return self._session.set_alarm_state('ArmAway')
