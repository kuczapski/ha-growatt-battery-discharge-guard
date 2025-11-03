"""GROWATT Battery Discharge Guard sensor platform."""

import logging
from datetime import datetime, timedelta
from typing import Any

from astral import LocationInfo
from astral.sun import sun

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTime, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    DOMAIN,
    ATTR_BATTERY_LEVEL,
    ATTR_IS_CHARGING,
    UNIT_KW,
    UNIT_KWH,
    UNIT_PERCENTAGE,
)

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
        SunsetTimeSensor(coordinator, config_entry, hass),
        SunsetCountdownSensor(coordinator, config_entry, hass),
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
        self.min_discharge_percentage = config_entry.data.get(
            "min_discharge_percentage", 10
        )

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
                self.growatt_username,
                self.pv_max_power,
                self.battery_capacity,
                self.min_discharge_percentage,
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
            "pv_max_power": {
                "value": self._config_entry.data.get("pv_max_power", 10.0),
                "unit": UNIT_KW,
            },
            "battery_capacity": {
                "value": self._config_entry.data.get("battery_capacity", 10.0),
                "unit": UNIT_KWH,
            },
            "min_discharge_percentage": {
                "value": self._config_entry.data.get("min_discharge_percentage", 10),
                "unit": UNIT_PERCENTAGE,
            },
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


class SunsetTimeSensor(SensorEntity):
    """Sensor showing the expected sunset time."""

    def __init__(
        self, coordinator: BatteryDataUpdateCoordinator, config_entry: ConfigEntry, hass
    ) -> None:
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.config_entry = config_entry
        self.hass = hass
        self._attr_name = f"{config_entry.data[CONF_NAME]} Sunset Time"
        self._attr_unique_id = f"{config_entry.entry_id}_sunset_time"
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_icon = "mdi:weather-sunset"

    @property
    def state(self) -> str | None:
        """Return the sunset time."""
        try:
            # Get Home Assistant's configured location
            latitude = self.hass.config.latitude
            longitude = self.hass.config.longitude
            timezone = self.hass.config.time_zone

            # Create location info
            location = LocationInfo("Home", "Home", timezone, latitude, longitude)

            # Calculate sunset for today
            today = datetime.now().date()
            s = sun(location.observer, date=today)

            return s["sunset"].isoformat()
        except Exception as e:
            _LOGGER.error("Error calculating sunset time: %s", e)
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        try:
            latitude = self.hass.config.latitude
            longitude = self.hass.config.longitude
            timezone = self.hass.config.time_zone

            location = LocationInfo("Home", "Home", timezone, latitude, longitude)
            today = datetime.now().date()
            s = sun(location.observer, date=today)

            return {
                "sunrise": s["sunrise"].isoformat(),
                "sunset": s["sunset"].isoformat(),
                "dawn": s["dawn"].isoformat(),
                "dusk": s["dusk"].isoformat(),
                "latitude": latitude,
                "longitude": longitude,
                "timezone": timezone,
            }
        except Exception as e:
            _LOGGER.error("Error calculating sun times: %s", e)
            return {}

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return True

    async def async_update(self) -> None:
        """Update the entity."""
        # This entity updates based on time/location, not coordinator data
        pass


class SunsetCountdownSensor(SensorEntity):
    """Sensor showing remaining time until sunset."""

    def __init__(
        self, coordinator: BatteryDataUpdateCoordinator, config_entry: ConfigEntry, hass
    ) -> None:
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.config_entry = config_entry
        self.hass = hass
        self._attr_name = f"{config_entry.data[CONF_NAME]} Time Until Sunset"
        self._attr_unique_id = f"{config_entry.entry_id}_time_until_sunset"
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_native_unit_of_measurement = "s"  # seconds
        self._attr_icon = "mdi:timer-sand"

    @property
    def state(self) -> float | None:
        """Return the time until sunset in seconds."""
        try:
            # Get Home Assistant's configured location
            latitude = self.hass.config.latitude
            longitude = self.hass.config.longitude
            timezone = self.hass.config.time_zone

            # Create location info
            location = LocationInfo("Home", "Home", timezone, latitude, longitude)

            # Calculate sunset for today
            today = datetime.now().date()
            s = sun(location.observer, date=today)
            sunset_time = s["sunset"]

            # Calculate time difference
            now = datetime.now(sunset_time.tzinfo)
            if sunset_time > now:
                time_diff = sunset_time - now
                return time_diff.total_seconds()
            else:
                # Sunset has passed, calculate for tomorrow
                tomorrow = today + timedelta(days=1)
                s_tomorrow = sun(location.observer, date=tomorrow)
                sunset_tomorrow = s_tomorrow["sunset"]
                time_diff = sunset_tomorrow - now
                return time_diff.total_seconds()

        except Exception as e:
            _LOGGER.error("Error calculating time until sunset: %s", e)
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        try:
            latitude = self.hass.config.latitude
            longitude = self.hass.config.longitude
            timezone = self.hass.config.time_zone

            location = LocationInfo("Home", "Home", timezone, latitude, longitude)
            today = datetime.now().date()
            s = sun(location.observer, date=today)
            sunset_time = s["sunset"]

            now = datetime.now(sunset_time.tzinfo)

            if sunset_time > now:
                time_diff = sunset_time - now
                hours = int(time_diff.total_seconds() // 3600)
                minutes = int((time_diff.total_seconds() % 3600) // 60)
                human_readable = f"{hours}h {minutes}m"
                next_sunset = sunset_time
            else:
                # Sunset has passed, show tomorrow's sunset
                tomorrow = today + timedelta(days=1)
                s_tomorrow = sun(location.observer, date=tomorrow)
                next_sunset = s_tomorrow["sunset"]
                time_diff = next_sunset - now
                hours = int(time_diff.total_seconds() // 3600)
                minutes = int((time_diff.total_seconds() % 3600) // 60)
                human_readable = f"{hours}h {minutes}m (tomorrow)"

            return {
                "next_sunset": next_sunset.isoformat(),
                "human_readable": human_readable,
                "hours_remaining": int(time_diff.total_seconds() // 3600),
                "minutes_remaining": int((time_diff.total_seconds() % 3600) // 60),
                "latitude": latitude,
                "longitude": longitude,
                "timezone": timezone,
            }
        except Exception as e:
            _LOGGER.error("Error calculating countdown attributes: %s", e)
            return {}

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return True

    async def async_update(self) -> None:
        """Update the entity."""
        # This entity updates based on time/location, not coordinator data
        pass
