"""Config flow for GROWATT Battery Discharge Guard integration."""

import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("name", default="GROWATT Battery Discharge Guard"): str,
        vol.Required("growatt_username"): str,
        vol.Required("growatt_password"): str,
        vol.Optional("pv_max_power", default=10.0): vol.Coerce(float),
        vol.Optional("battery_capacity", default=10.0): vol.Coerce(float),
        vol.Optional("min_discharge_percentage", default=10): cv.positive_int,
        vol.Optional("update_interval", default=30): cv.positive_int,
        vol.Optional("low_battery_threshold", default=20): cv.positive_int,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GROWATT Battery Discharge Guard."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate the user input
            if user_input["low_battery_threshold"] > 100:
                errors["low_battery_threshold"] = "threshold_too_high"
            elif user_input["min_discharge_percentage"] > 100:
                errors["min_discharge_percentage"] = "discharge_too_high"
            elif user_input["min_discharge_percentage"] < 0:
                errors["min_discharge_percentage"] = "discharge_too_low"
            elif user_input["pv_max_power"] <= 0:
                errors["pv_max_power"] = "power_invalid"
            elif user_input["battery_capacity"] <= 0:
                errors["battery_capacity"] = "capacity_invalid"
            elif not user_input.get("growatt_username"):
                errors["growatt_username"] = "username_required"
            elif not user_input.get("growatt_password"):
                errors["growatt_password"] = "password_required"
            else:
                # Create the config entry
                return self.async_create_entry(
                    title=user_input["name"],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "growatt_username",
                        default=self.config_entry.data.get("growatt_username", ""),
                    ): str,
                    vol.Optional(
                        "growatt_password",
                        default=self.config_entry.data.get("growatt_password", ""),
                    ): str,
                    vol.Optional(
                        "pv_max_power",
                        default=self.config_entry.data.get("pv_max_power", 10.0),
                    ): vol.Coerce(float),
                    vol.Optional(
                        "battery_capacity",
                        default=self.config_entry.data.get("battery_capacity", 10.0),
                    ): vol.Coerce(float),
                    vol.Optional(
                        "min_discharge_percentage",
                        default=self.config_entry.data.get(
                            "min_discharge_percentage", 10
                        ),
                    ): cv.positive_int,
                    vol.Optional(
                        "update_interval",
                        default=self.config_entry.options.get("update_interval", 30),
                    ): cv.positive_int,
                    vol.Optional(
                        "low_battery_threshold",
                        default=self.config_entry.options.get(
                            "low_battery_threshold", 20
                        ),
                    ): cv.positive_int,
                }
            ),
        )
