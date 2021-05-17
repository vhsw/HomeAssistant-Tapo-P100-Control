"""Tapo P100 Home Assistant Intergration"""
import logging
from dataclasses import asdict

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchEntity
from homeassistant.const import CONF_EMAIL, CONF_IP_ADDRESS, CONF_PASSWORD

from .device_info import DeviceInfo
from .p100 import P100

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_IP_ADDRESS): cv.string,
        vol.Required(CONF_EMAIL): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }
)

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Awesome Light platform."""
    # Assign configuration variables.
    # The configuration check takes care they are present.
    ip_address = config[CONF_IP_ADDRESS]
    email = config[CONF_EMAIL]
    password = config.get(CONF_PASSWORD)

    # Setup connection with devices/cloud
    add_entities([P100Plug(ip_address, email, password)])


class P100Plug(SwitchEntity):
    """Representation of a P100 Plug"""

    def __init__(self, ip_address, email, password):
        self.p100 = P100(ip_address, email, password)
        self._device_info = DeviceInfo()

    def turn_on(self, **kwargs) -> None:
        """Turn Plug On"""
        self.p100.turn_on()

    def turn_off(self, **kwargs):
        """Turn Plug Off"""
        self.p100.turn_off()

    def update(self):
        self._device_info = self.p100.device_info()

    @property
    def is_on(self):
        return self._device_info.device_on

    @property
    def name(self):
        return self._device_info.nickname

    @property
    def device_info(self):
        return asdict(self._device_info)

    @property
    def device_class(self):
        return "outlet"

    @property
    def unique_id(self):
        return self._device_info.device_id
