"""GROWATT Battery Discharge Guard sensor platform."""

import logging
from datetime import timedelta
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN, ATTR_BATTERY_LEVEL, ATTR_IS_CHARGING

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the GROWATT Battery Discharge Guard sensor platform."""

    # Create coordinator for data updates
    coordinator = BatteryDataUpdateCoordinator(hass, config_entry)
    await coordinator.async_config_entry_first_refresh()

    # Create sensor entities
    entities = [
        BatteryLevelSensor(coordinator, config_entry),
        BatteryChargingSensor(coordinator, config_entry),
    ]

    async_add_entities(entities)


class BatteryDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching battery data."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        update_interval = timedelta(
            seconds=config_entry.data.get("update_interval", 30)
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.config_entry = config_entry
        self.growatt_username = config_entry.data.get("growatt_username")
        self.growatt_password = config_entry.data.get("growatt_password")
        self.pv_max_power = config_entry.data.get("pv_max_power", 10.0)
        self.battery_capacity = config_entry.data.get("battery_capacity", 10.0)
        self.min_discharge_percentage = config_entry.data.get("min_discharge_percentage", 10)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch battery data."""
        try:
            # TODO: Implement actual GROWATT API communication using:
            # self.growatt_username and self.growatt_password
            # Configuration values available:
            # self.pv_max_power (kW), self.battery_capacity (kWh), self.min_discharge_percentage (%)
            # For now, we'll simulate battery data
            _LOGGER.debug(
                "Fetching battery data for GROWATT user: %s (PV: %skW, Battery: %skWh, Min discharge: %s%%)", 
                self.growatt_username, self.pv_max_power, self.battery_capacity, self.min_discharge_percentage
            )
            return {
                ATTR_BATTERY_LEVEL: 85,  # Simulated battery level
                ATTR_IS_CHARGING: False,  # Simulated charging status
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with GROWATT server: {err}")


class BatteryLevelSensor(CoordinatorEntity, SensorEntity):
    """Battery level sensor."""

    def __init__(
        self,
        coordinator: BatteryDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_name = (
            f"{config_entry.data.get('name', 'GROWATT Battery Discharge Guard')} Level"
        )
        self._attr_unique_id = f"{config_entry.entry_id}_battery_level"
        self._attr_device_class = SensorDeviceClass.BATTERY
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int:
        """Return the battery level."""
        return self.coordinator.data.get(ATTR_BATTERY_LEVEL)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        return {
            "threshold": self._config_entry.data.get("low_battery_threshold", 20),
            "is_low": self.native_value
            < self._config_entry.data.get("low_battery_threshold", 20),
            "pv_max_power_kw": self._config_entry.data.get("pv_max_power", 10.0),
            "battery_capacity_kwh": self._config_entry.data.get("battery_capacity", 10.0),
            "min_discharge_percentage": self._config_entry.data.get("min_discharge_percentage", 10),
        }


class BatteryChargingSensor(CoordinatorEntity, SensorEntity):
    """Battery charging status sensor."""

    def __init__(
        self,
        coordinator: BatteryDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_name = f"{config_entry.data.get('name', 'GROWATT Battery Discharge Guard')} Charging"
        self._attr_unique_id = f"{config_entry.entry_id}_battery_charging"
        self._attr_device_class = SensorDeviceClass.ENUM
        self._attr_options = ["charging", "not_charging", "unknown"]

    @property
    def native_value(self) -> str:
        """Return the charging status."""
        is_charging = self.coordinator.data.get(ATTR_IS_CHARGING)
        if is_charging is None:
            return "unknown"
        return "charging" if is_charging else "not_charging"
