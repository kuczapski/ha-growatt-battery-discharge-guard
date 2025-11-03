"""GROWATT Battery Discharge Guard sensor platform."""

import logging
import math
from datetime import datetime, timedelta
from typing import Any

# Import astral library (compatible with Home Assistant's included version 2.2)
try:
    # For astral >= 2.0
    from astral import LocationInfo
    from astral.sun import sun

    ASTRAL_V2 = True
except ImportError:
    # Fallback for older astral versions
    from astral import Astral, Location

    ASTRAL_V2 = False

    ASTRAL_V2 = False


def get_sun_times(latitude: float, longitude: float, timezone: str, date) -> dict:
    """Get sun times using appropriate astral version."""
    try:
        if ASTRAL_V2:
            # Use astral 2.x API
            location = LocationInfo("Home", "Home", timezone, latitude, longitude)
            return sun(location.observer, date=date)
        else:
            # Use astral 1.x API (fallback)
            astral = Astral()
            location = Location()
            location.latitude = latitude
            location.longitude = longitude
            location.timezone = timezone
            return astral.sun_utc(date, location.latitude, location.longitude)
    except Exception as e:
        _LOGGER.error("Error calculating sun times: %s", e)
        return {}


def calculate_solar_position(latitude: float, longitude: float, dt: datetime) -> dict:
    """Calculate solar elevation and azimuth for a given time and location."""
    try:
        # Convert to Julian day
        a = (14 - dt.month) // 12
        y = dt.year - a
        m = dt.month + 12 * a - 3
        jd = (
            dt.day
            + (153 * m + 2) // 5
            + 365 * y
            + y // 4
            - y // 100
            + y // 400
            + 1721119
        )

        # Add time of day
        jd += (dt.hour - 12) / 24.0 + dt.minute / 1440.0 + dt.second / 86400.0

        # Calculate solar position
        n = jd - 2451545.0
        L = (280.460 + 0.9856474 * n) % 360
        g = math.radians((357.528 + 0.9856003 * n) % 360)
        lambda_sun = math.radians(L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g))

        # Declination
        delta = math.asin(math.sin(math.radians(23.439)) * math.sin(lambda_sun))

        # Hour angle
        lat_rad = math.radians(latitude)
        lon_rad = math.radians(longitude)

        # Mean solar time
        mst = dt.hour + dt.minute / 60.0 + dt.second / 3600.0

        # Hour angle
        h = math.radians(15 * (mst - 12) + longitude)

        # Solar elevation
        elevation = math.asin(
            math.sin(lat_rad) * math.sin(delta)
            + math.cos(lat_rad) * math.cos(delta) * math.cos(h)
        )

        # Solar azimuth
        azimuth = math.atan2(
            math.sin(h),
            math.cos(h) * math.sin(lat_rad) - math.tan(delta) * math.cos(lat_rad),
        )

        return {
            "elevation": math.degrees(elevation),
            "azimuth": math.degrees(azimuth) % 360,
        }
    except Exception as e:
        _LOGGER.error("Error calculating solar position: %s", e)
        return {"elevation": 0, "azimuth": 0}


def calculate_panel_irradiance(
    solar_elevation: float,
    solar_azimuth: float,
    panel_tilt: float,
    panel_azimuth: float,
) -> float:
    """Calculate irradiance on tilted panel surface."""
    try:
        # Convert to radians
        sun_el = math.radians(max(0, solar_elevation))
        sun_az = math.radians(solar_azimuth)
        panel_tilt_rad = math.radians(panel_tilt)
        panel_az_rad = math.radians(panel_azimuth)

        # Calculate angle of incidence
        cos_incidence = math.sin(sun_el) * math.cos(panel_tilt_rad) + math.cos(
            sun_el
        ) * math.sin(panel_tilt_rad) * math.cos(sun_az - panel_az_rad)

        # Ensure non-negative
        cos_incidence = max(0, cos_incidence)

        # Direct normal irradiance (simplified clear sky model)
        # This is a simplified model - in reality you'd use weather data
        if solar_elevation > 0:
            # Atmospheric transmission (simplified)
            air_mass = 1 / math.sin(sun_el) if solar_elevation > 1 else 10
            transmission = 0.7 ** (air_mass**0.678)

            # Direct normal irradiance (W/m²)
            dni = 900 * transmission  # Simplified clear sky model

            # Irradiance on panel surface
            panel_irradiance = dni * cos_incidence
        else:
            panel_irradiance = 0

        return max(0, panel_irradiance)
    except Exception as e:
        _LOGGER.error("Error calculating panel irradiance: %s", e)
        return 0


def calculate_energy_forecast(
    latitude: float,
    longitude: float,
    timezone: str,
    panel_tilt: float,
    panel_orientation: float,
    pv_max_power: float,
    start_time: datetime = None,
) -> dict:
    """Calculate energy production forecast in 5-minute intervals until sunset."""
    try:
        if start_time is None:
            start_time = datetime.now()

        today = start_time.date()
        sun_times = get_sun_times(latitude, longitude, timezone, today)

        if not sun_times or "sunset" not in sun_times or "sunrise" not in sun_times:
            return {
                "total_energy": 0,
                "forecast": [],
                "full_day_forecast": [],
                "total_daily_energy": 0,
            }

        sunrise_time = sun_times["sunrise"]
        sunset_time = sun_times["sunset"]

        # Check if we're past sunset - if so, calculate for tomorrow
        forecast_day = today
        if start_time >= sunset_time:
            _LOGGER.info("Past sunset, calculating forecast for tomorrow")
            tomorrow = today + timedelta(days=1)
            tomorrow_sun_times = get_sun_times(latitude, longitude, timezone, tomorrow)
            
            if tomorrow_sun_times and "sunrise" in tomorrow_sun_times and "sunset" in tomorrow_sun_times:
                sunrise_time = tomorrow_sun_times["sunrise"]
                sunset_time = tomorrow_sun_times["sunset"]
                forecast_day = tomorrow
                _LOGGER.info(f"Using tomorrow's times: sunrise={sunrise_time}, sunset={sunset_time}")
            else:
                # Fallback to today's data if tomorrow calculation fails
                _LOGGER.warning("Could not calculate tomorrow's sun times, using today's")
                forecast_day = today

        # Calculate full day forecast (sunrise to sunset)
        full_day_forecast = []
        total_daily_energy = 0
        current_time_full = sunrise_time

        _LOGGER.debug(f"Calculating forecast from {sunrise_time} to {sunset_time} for {forecast_day}")

        while current_time_full < sunset_time:
            # Get solar position
            solar_pos = calculate_solar_position(latitude, longitude, current_time_full)

            # Only include intervals where sun is above horizon
            if solar_pos["elevation"] > 0:
            # Only include intervals where sun is above horizon
            if solar_pos["elevation"] > 0:
                # Calculate panel irradiance
                irradiance = calculate_panel_irradiance(
                    solar_pos["elevation"],
                    solar_pos["azimuth"],
                    panel_tilt,
                    panel_orientation,
                )

                # Calculate power output (simplified)
                # Assume 20% panel efficiency and 90% system efficiency
                panel_efficiency = 0.20
                system_efficiency = 0.90

                # Power in kW (assuming pv_max_power is the panel area equivalent)
                power_kw = (
                    (irradiance / 1000)
                    * pv_max_power
                    * panel_efficiency
                    * system_efficiency
                )

                # Energy in 5 minutes (kWh)
                energy_5min = power_kw * (5 / 60)  # 5 minutes = 1/12 hour

                full_day_forecast.append(
                    {
                        "time": current_time_full.isoformat(),
                        "solar_elevation": round(solar_pos["elevation"], 2),
                        "solar_azimuth": round(solar_pos["azimuth"], 2),
                        "irradiance": round(irradiance, 2),
                        "power_kw": round(power_kw, 3),
                        "energy_5min_kwh": round(energy_5min, 4),
                    }
                )

                total_daily_energy += energy_5min
            current_time_full += timedelta(minutes=5)

        # Determine if we need to calculate remaining forecast
        original_sunset = get_sun_times(latitude, longitude, start_time.date()).get("sunset") if get_sun_times(latitude, longitude, start_time.date()) else sunset_time
        
        # If we're past today's sunset, there's no remaining energy for today
        if start_time >= original_sunset:
            return {
                "total_energy": 0,
                "forecast": [],
                "full_day_forecast": full_day_forecast,
                "total_daily_energy": round(total_daily_energy, 3),
                "sunrise_time": sunrise_time.isoformat(),
                "sunset_time": sunset_time.isoformat(),
                "forecast_start": start_time.isoformat(),
                "forecast_day": forecast_day.isoformat() if 'forecast_day' in locals() else today.isoformat(),
            }

        # Calculate remaining forecast (from now until sunset)
        forecast = []
        total_energy = 0
        current_time = start_time

        # Calculate in 5-minute intervals until sunset
        while current_time < sunset_time:
            # Get solar position
            solar_pos = calculate_solar_position(latitude, longitude, current_time)

            # Calculate panel irradiance
            irradiance = calculate_panel_irradiance(
                solar_pos["elevation"],
                solar_pos["azimuth"],
                panel_tilt,
                panel_orientation,
            )

            # Calculate power output (simplified)
            # Assume 20% panel efficiency and 90% system efficiency
            panel_efficiency = 0.20
            system_efficiency = 0.90

            # Power in kW (assuming pv_max_power is the panel area equivalent)
            power_kw = (
                (irradiance / 1000)
                * pv_max_power
                * panel_efficiency
                * system_efficiency
            )

            # Energy in 5 minutes (kWh)
            energy_5min = power_kw * (5 / 60)  # 5 minutes = 1/12 hour

            forecast.append(
                {
                    "time": current_time.isoformat(),
                    "solar_elevation": round(solar_pos["elevation"], 2),
                    "solar_azimuth": round(solar_pos["azimuth"], 2),
                    "irradiance": round(irradiance, 2),
                    "power_kw": round(power_kw, 3),
                    "energy_5min_kwh": round(energy_5min, 4),
                }
            )

            total_energy += energy_5min
            current_time += timedelta(minutes=5)

        return {
            "total_energy": round(total_energy, 3),
            "forecast": forecast,
            "full_day_forecast": full_day_forecast,
            "total_daily_energy": round(total_daily_energy, 3),
            "sunrise_time": sunrise_time.isoformat(),
            "sunset_time": sunset_time.isoformat(),
            "forecast_start": start_time.isoformat(),
            "forecast_day": forecast_day.isoformat() if 'forecast_day' in locals() else today.isoformat(),
        }

    except Exception as e:
        _LOGGER.error("Error calculating energy forecast: %s", e)
        return {
            "total_energy": 0,
            "forecast": [],
            "full_day_forecast": [],
            "total_daily_energy": 0,
        }


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
    UNIT_DEGREES,
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
        SolarEnergyForecastSensor(coordinator, config_entry, hass),
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
        self.panel_tilt_angle = config_entry.data.get("panel_tilt_angle", 30.0)
        self.panel_orientation = config_entry.data.get("panel_orientation", 180.0)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch battery data."""
        try:
            # TODO: Implement actual GROWATT API communication using:
            # self.growatt_username and self.growatt_password
            # Configuration values available:
            # self.pv_max_power (kW), self.battery_capacity (kWh), self.min_discharge_percentage (%)
            # self.panel_tilt_angle (°), self.panel_orientation (°)
            # For now, we'll simulate battery data
            _LOGGER.debug(
                "Fetching battery data for GROWATT user: %s (PV: %skW, Battery: %skWh, Min discharge: %s%%, Panel tilt: %s°, Orientation: %s°)",
                self.growatt_username,
                self.pv_max_power,
                self.battery_capacity,
                self.min_discharge_percentage,
                self.panel_tilt_angle,
                self.panel_orientation,
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
            "panel_tilt_angle": {
                "value": self._config_entry.data.get("panel_tilt_angle", 30.0),
                "unit": UNIT_DEGREES,
            },
            "panel_orientation": {
                "value": self._config_entry.data.get("panel_orientation", 180.0),
                "unit": UNIT_DEGREES,
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

            # Calculate sunset for today
            today = datetime.now().date()
            s = get_sun_times(latitude, longitude, timezone, today)

            if s and "sunset" in s:
                return s["sunset"].isoformat()
            return None
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

            today = datetime.now().date()
            s = get_sun_times(latitude, longitude, timezone, today)

            if s:
                attributes = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "timezone": timezone,
                }

                # Add sun times if available
                for key in ["sunrise", "sunset", "dawn", "dusk"]:
                    if key in s and s[key]:
                        attributes[key] = s[key].isoformat()

                return attributes

            return {
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

            # Calculate sunset for today
            today = datetime.now().date()
            s = get_sun_times(latitude, longitude, timezone, today)

            if not s or "sunset" not in s or "sunrise" not in s:
                return None

            sunset_time = s["sunset"]
            sunrise_time = s["sunrise"]

            # Calculate time difference
            now = datetime.now(sunset_time.tzinfo)

            if sunset_time > now:
                # Before sunset today - return time until sunset
                time_diff = sunset_time - now
                return time_diff.total_seconds()
            else:
                # After sunset - check if we're before tomorrow's sunrise
                tomorrow = today + timedelta(days=1)
                s_tomorrow = get_sun_times(latitude, longitude, timezone, tomorrow)
                if s_tomorrow and "sunrise" in s_tomorrow:
                    sunrise_tomorrow = s_tomorrow["sunrise"]
                    if now < sunrise_tomorrow:
                        # It's nighttime (between sunset and sunrise) - return 0
                        return 0.0

                # After sunrise - calculate time until next sunset
                if s_tomorrow and "sunset" in s_tomorrow:
                    sunset_tomorrow = s_tomorrow["sunset"]
                    time_diff = sunset_tomorrow - now
                    return time_diff.total_seconds()
                return None

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

            today = datetime.now().date()
            s = get_sun_times(latitude, longitude, timezone, today)

            if not s or "sunset" not in s or "sunrise" not in s:
                return {
                    "latitude": latitude,
                    "longitude": longitude,
                    "timezone": timezone,
                }

            sunset_time = s["sunset"]
            sunrise_time = s["sunrise"]
            now = datetime.now(sunset_time.tzinfo)

            if sunset_time > now:
                # Before sunset today - show time until sunset
                time_diff = sunset_time - now
                hours = int(time_diff.total_seconds() // 3600)
                minutes = int((time_diff.total_seconds() % 3600) // 60)
                human_readable = f"{hours}h {minutes}m"
                next_sunset = sunset_time

                return {
                    "next_sunset": next_sunset.isoformat(),
                    "human_readable": human_readable,
                    "hours_remaining": hours,
                    "minutes_remaining": minutes,
                    "is_nighttime": False,
                    "latitude": latitude,
                    "longitude": longitude,
                    "timezone": timezone,
                }
            else:
                # After sunset - check if we're before tomorrow's sunrise
                tomorrow = today + timedelta(days=1)
                s_tomorrow = get_sun_times(latitude, longitude, timezone, tomorrow)

                if s_tomorrow and "sunrise" in s_tomorrow:
                    sunrise_tomorrow = s_tomorrow["sunrise"]
                    if now < sunrise_tomorrow:
                        # It's nighttime (between sunset and sunrise) - show 0
                        return {
                            "next_sunset": (
                                s_tomorrow.get("sunset", sunset_time).isoformat()
                                if s_tomorrow
                                else sunset_time.isoformat()
                            ),
                            "human_readable": "0h 0m (nighttime)",
                            "hours_remaining": 0,
                            "minutes_remaining": 0,
                            "is_nighttime": True,
                            "latitude": latitude,
                            "longitude": longitude,
                            "timezone": timezone,
                        }

                # After sunrise - show time until next sunset
                if s_tomorrow and "sunset" in s_tomorrow:
                    next_sunset = s_tomorrow["sunset"]
                    time_diff = next_sunset - now
                    hours = int(time_diff.total_seconds() // 3600)
                    minutes = int((time_diff.total_seconds() % 3600) // 60)
                    human_readable = f"{hours}h {minutes}m"

                    return {
                        "next_sunset": next_sunset.isoformat(),
                        "human_readable": human_readable,
                        "hours_remaining": hours,
                        "minutes_remaining": minutes,
                        "is_nighttime": False,
                        "latitude": latitude,
                        "longitude": longitude,
                        "timezone": timezone,
                    }
                else:
                    return {
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


class SolarEnergyForecastSensor(SensorEntity):
    """Sensor showing forecasted solar energy production until sunset."""

    def __init__(
        self, coordinator: BatteryDataUpdateCoordinator, config_entry: ConfigEntry, hass
    ) -> None:
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.config_entry = config_entry
        self.hass = hass
        self._attr_name = f"{config_entry.data[CONF_NAME]} Solar Energy Forecast"
        self._attr_unique_id = f"{config_entry.entry_id}_solar_energy_forecast"
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_native_unit_of_measurement = "kWh"
        self._attr_state_class = SensorStateClass.TOTAL
        self._attr_icon = "mdi:solar-power"

    @property
    def state(self) -> float | None:
        """Return the forecasted energy production until sunset."""
        try:
            # Get Home Assistant's configured location
            latitude = self.hass.config.latitude
            longitude = self.hass.config.longitude
            timezone = self.hass.config.time_zone

            # Get solar panel configuration
            panel_tilt = self.config_entry.data.get("panel_tilt_angle", 30.0)
            panel_orientation = self.config_entry.data.get("panel_orientation", 180.0)
            pv_max_power = self.config_entry.data.get("pv_max_power", 10.0)

            # Calculate forecast
            forecast_data = calculate_energy_forecast(
                latitude=latitude,
                longitude=longitude,
                timezone=timezone,
                panel_tilt=panel_tilt,
                panel_orientation=panel_orientation,
                pv_max_power=pv_max_power,
            )

            return forecast_data.get("total_energy", 0)

        except Exception as e:
            _LOGGER.error("Error calculating solar energy forecast: %s", e)
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes with detailed forecast."""
        try:
            # Get Home Assistant's configured location
            latitude = self.hass.config.latitude
            longitude = self.hass.config.longitude
            timezone = self.hass.config.time_zone

            # Get solar panel configuration
            panel_tilt = self.config_entry.data.get("panel_tilt_angle", 30.0)
            panel_orientation = self.config_entry.data.get("panel_orientation", 180.0)
            pv_max_power = self.config_entry.data.get("pv_max_power", 10.0)

            # Calculate forecast
            forecast_data = calculate_energy_forecast(
                latitude=latitude,
                longitude=longitude,
                timezone=timezone,
                panel_tilt=panel_tilt,
                panel_orientation=panel_orientation,
                pv_max_power=pv_max_power,
            )

            # Prepare attributes
            attributes = {
                "total_energy_kwh": forecast_data.get("total_energy", 0),
                "forecast_intervals": len(forecast_data.get("forecast", [])),
                "total_daily_energy_kwh": forecast_data.get("total_daily_energy", 0),
                "full_day_intervals": len(forecast_data.get("full_day_forecast", [])),
                "panel_tilt_angle": panel_tilt,
                "panel_orientation": panel_orientation,
                "pv_max_power_kw": pv_max_power,
                "latitude": latitude,
                "longitude": longitude,
                "timezone": timezone,
            }

            # Add forecast data (remaining energy from now until sunset)
            if "forecast" in forecast_data:
                attributes["forecast_5min_intervals"] = forecast_data["forecast"]

            # Add full day forecast data (sunrise to sunset)
            if "full_day_forecast" in forecast_data:
                attributes["full_day_forecast_5min_intervals"] = forecast_data[
                    "full_day_forecast"
                ]

            # Add time information
            if "sunrise_time" in forecast_data:
                attributes["sunrise_time"] = forecast_data["sunrise_time"]

            if "sunset_time" in forecast_data:
                attributes["sunset_time"] = forecast_data["sunset_time"]

            if "forecast_start" in forecast_data:
                attributes["forecast_start"] = forecast_data["forecast_start"]

            if "forecast_day" in forecast_data:
                attributes["forecast_day"] = forecast_data["forecast_day"]

            # Add summary statistics for remaining forecast
            forecast = forecast_data.get("forecast", [])
            if forecast:
                # Calculate peak power time from remaining forecast
                max_power_entry = max(forecast, key=lambda x: x.get("power_kw", 0))
                attributes["peak_power_time_remaining"] = max_power_entry.get("time")
                attributes["peak_power_kw_remaining"] = max_power_entry.get(
                    "power_kw", 0
                )

                # Calculate average power for remaining forecast
                total_power = sum(entry.get("power_kw", 0) for entry in forecast)
                attributes["average_power_kw_remaining"] = (
                    round(total_power / len(forecast), 3) if forecast else 0
                )

            # Add summary statistics for full day forecast
            full_day_forecast = forecast_data.get("full_day_forecast", [])
            if full_day_forecast:
                # Calculate peak power time for full day
                max_power_entry_day = max(
                    full_day_forecast, key=lambda x: x.get("power_kw", 0)
                )
                attributes["peak_power_time_daily"] = max_power_entry_day.get("time")
                attributes["peak_power_kw_daily"] = max_power_entry_day.get(
                    "power_kw", 0
                )

                # Calculate average power for full day
                total_power_day = sum(
                    entry.get("power_kw", 0) for entry in full_day_forecast
                )
                attributes["average_power_kw_daily"] = (
                    round(total_power_day / len(full_day_forecast), 3)
                    if full_day_forecast
                    else 0
                )

            return attributes

        except Exception as e:
            _LOGGER.error("Error calculating forecast attributes: %s", e)
            return {
                "error": "Failed to calculate forecast",
                "panel_tilt_angle": self.config_entry.data.get(
                    "panel_tilt_angle", 30.0
                ),
                "panel_orientation": self.config_entry.data.get(
                    "panel_orientation", 180.0
                ),
                "pv_max_power_kw": self.config_entry.data.get("pv_max_power", 10.0),
            }

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return True

    async def async_update(self) -> None:
        """Update the entity."""
        # This entity updates based on time/location/configuration, not coordinator data
        pass
