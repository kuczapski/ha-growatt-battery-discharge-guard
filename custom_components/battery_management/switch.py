"""GROWATT Battery Discharge Guard switch platform."""

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the GROWATT Battery Discharge Guard switch platform."""

    # Create switch entities
    entities = [
        BatteryManagementSwitch(config_entry),
        BatteryOptimizationSwitch(config_entry),
    ]

    async_add_entities(entities)


class BatteryManagementSwitch(SwitchEntity):
    """Battery management main switch."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the switch."""
        self._config_entry = config_entry
        self._attr_name = f"{config_entry.data.get('name', 'GROWATT Battery Discharge Guard')} Enabled"
        self._attr_unique_id = f"{config_entry.entry_id}_enabled"
        self._is_on = True

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return self._is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        self._is_on = True
        _LOGGER.info("Battery management enabled")
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        self._is_on = False
        _LOGGER.info("Battery management disabled")
        self.async_write_ha_state()


class BatteryOptimizationSwitch(SwitchEntity):
    """Battery optimization switch."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the switch."""
        self._config_entry = config_entry
        self._attr_name = f"{config_entry.data.get('name', 'GROWATT Battery Discharge Guard')} Optimization"
        self._attr_unique_id = f"{config_entry.entry_id}_optimization"
        self._is_on = False

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return self._is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        self._is_on = True
        _LOGGER.info("Battery optimization enabled")
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        self._is_on = False
        _LOGGER.info("Battery optimization disabled")
        self.async_write_ha_state()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        return {
            "optimization_mode": "balanced" if self._is_on else "disabled",
            "power_saving": self._is_on,
        }
