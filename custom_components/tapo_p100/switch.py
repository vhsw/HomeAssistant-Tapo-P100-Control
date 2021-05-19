"""Tapo P100 Home Assistant Intergration"""
import logging
from typing import Callable

from homeassistant.components.switch import DEVICE_CLASS_OUTLET, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_IP_ADDRESS, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .device_info import DeviceInfo
from .p100 import P100

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: Callable,
):
    """Setup sensors from a config entry created in the integrations UI."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    p100 = P100(
        address=config[CONF_IP_ADDRESS],
        email=config[CONF_EMAIL],
        password=config[CONF_PASSWORD],
        session=async_get_clientsession(hass),
    )

    async_add_entities([P100Plug(p100)], update_before_add=True)


class P100Plug(SwitchEntity):
    """Representation of a P100 Plug"""

    def __init__(self, p100: P100):
        self.p100 = p100
        self._device_info = DeviceInfo()

    async def async_turn_on(self, **kwargs) -> None:
        """Turn Plug On"""
        await self.p100.turn_on()

    async def async_turn_off(self, **kwargs):
        """Turn Plug Off"""
        await self.p100.turn_off()

    async def async_update(self):
        """Update handler"""
        self._device_info = await self.p100.device_info()

    @property
    def is_on(self):
        return self._device_info.device_on

    @property
    def name(self):
        return self._device_info.nickname

    @property
    def device_info(self):
        info = self._device_info
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.name,
            "manufacturer": "TP-Link",
            "model": info.model,
            "hw_version": info.hw_ver,
            "sw_version": info.fw_ver,
            "mac": info.mac,
        }

    @property
    def extra_state_attributes(self):
        info = self._device_info
        return {
            "on_time": info.on_time,
            "ip_address": info.ip,
            "rssi": info.rssi,
            "signal_level": info.signal_level,
            "overheated": info.overheated,
        }

    @property
    def device_class(self):
        return DEVICE_CLASS_OUTLET

    @property
    def unique_id(self):
        return self._device_info.device_id
