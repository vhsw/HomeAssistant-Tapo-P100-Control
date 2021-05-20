"""Config flow for Tapo P100 integration."""
import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_IP_ADDRESS, CONF_PASSWORD

from .const import DOMAIN, NAME
from .discover import discover

_LOGGER = logging.getLogger(__name__)


async def validate_input(_: dict):
    """Validate the user input allows us to connect."""
    # TODO: add validation


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore
    """Handle a config flow for P100."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        try:
            ip_address = discover()["ip"]
        except TimeoutError:
            ip_address = ""
        schema = vol.Schema(
            {
                vol.Required(CONF_IP_ADDRESS, default=ip_address): str,
                vol.Required(CONF_EMAIL): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )
        errors = {}
        if user_input is not None:
            try:
                await validate_input(user_input)
                return self.async_create_entry(title=NAME, data=user_input)
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including
        #  any errors that were found with the input.
        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
