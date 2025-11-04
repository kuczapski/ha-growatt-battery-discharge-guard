#!/usr/bin/env python3
"""
Standalone test script for solar energy forecast.
This script runs locally and prints the complete forecast for today.
"""

import sys
import os
from datetime import datetime, timedelta, timezone
import math
import logging

# Add the custom components path
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "custom_components", "battery_management"),
)

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
_LOGGER = logging.getLogger(__name__)


def mock_astral_functions():
    """Mock the astral library functions for standalone testing."""

    def get_sun_times(
        latitude: float, longitude: float, timezone_str: str, date
    ) -> dict:
        """Calculate sun times using basic astronomical formulas."""
        try:
            # Import astral if available
            from astral import LocationInfo
            from astral.sun import sun

            location = LocationInfo("Test", "Test", timezone_str, latitude, longitude)
            return sun(location.observer, date=date)
        except ImportError:
            # Fallback calculation if astral is not available
            _LOGGER.warning("Astral library not available, using basic calculations")
            return calculate_sun_times_basic(latitude, longitude, date)

    def calculate_sun_times_basic(latitude: float, longitude: float, date) -> dict:
        """Basic sun time calculations."""
        # This is a simplified calculation - in real use, astral library is much more accurate

        # Julian day number
        a = (14 - date.month) // 12
        y = date.year + 4800 - a
        m = date.month + 12 * a - 3
        jdn = (
            date.day
            + (153 * m + 2) // 5
            + 365 * y
            + y // 4
            - y // 100
            + y // 400
            - 32045
        )

        # Solar declination (simplified)
        day_of_year = date.timetuple().tm_yday
        declination = math.radians(
            23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365))
        )

        # Latitude in radians
        lat_rad = math.radians(latitude)

        # Hour angle for sunrise/sunset
        cos_hour_angle = -math.tan(lat_rad) * math.tan(declination)

        # Check for polar day/night
        if cos_hour_angle > 1:
            # Polar night
            return {}
        elif cos_hour_angle < -1:
            # Polar day
            return {}

        hour_angle = math.acos(cos_hour_angle)

        # Convert to hours
        sunrise_hour = 12 - math.degrees(hour_angle) / 15
        sunset_hour = 12 + math.degrees(hour_angle) / 15

        # Create timezone-aware datetime objects
        from datetime import timezone as dt_timezone

        tz = dt_timezone.utc  # Using UTC for simplicity

        sunrise = datetime.combine(date, datetime.min.time()).replace(
            hour=int(sunrise_hour), minute=int((sunrise_hour % 1) * 60), tzinfo=tz
        )
        sunset = datetime.combine(date, datetime.min.time()).replace(
            hour=int(sunset_hour), minute=int((sunset_hour % 1) * 60), tzinfo=tz
        )

        return {
            "sunrise": sunrise,
            "sunset": sunset,
            "dawn": sunrise - timedelta(minutes=30),
            "dusk": sunset + timedelta(minutes=30),
        }

    return get_sun_times


def mock_solar_calculations():
    """Mock the solar calculation functions."""

    def calculate_solar_position(
        latitude: float, longitude: float, dt: datetime
    ) -> dict:
        """Calculate solar elevation and azimuth for a given time and location."""
        try:
            # Convert to UTC if timezone-aware
            if dt.tzinfo:
                dt_utc = dt.utctimetuple()
                dt_local = datetime(
                    dt_utc.tm_year,
                    dt_utc.tm_mon,
                    dt_utc.tm_mday,
                    dt_utc.tm_hour,
                    dt_utc.tm_min,
                    dt_utc.tm_sec,
                )
            else:
                dt_local = dt

            # Day of year
            day_of_year = dt_local.timetuple().tm_yday

            # Solar declination (degrees)
            declination = 23.45 * math.sin(
                math.radians(360 * (284 + day_of_year) / 365)
            )

            # Hour angle from solar noon (degrees)
            # Adjust for longitude and timezone
            time_of_day = (
                dt_local.hour + dt_local.minute / 60.0 + dt_local.second / 3600.0
            )
            solar_time = time_of_day + longitude / 15.0  # Longitude correction
            hour_angle = 15 * (solar_time - 12)  # degrees from solar noon

            # Convert to radians
            lat_rad = math.radians(latitude)
            dec_rad = math.radians(declination)
            hour_rad = math.radians(hour_angle)

            # Solar elevation
            elevation = math.asin(
                math.sin(lat_rad) * math.sin(dec_rad)
                + math.cos(lat_rad) * math.cos(dec_rad) * math.cos(hour_rad)
            )

            # Solar azimuth
            azimuth = math.atan2(
                math.sin(hour_rad),
                math.cos(hour_rad) * math.sin(lat_rad)
                - math.tan(dec_rad) * math.cos(lat_rad),
            )

            return {
                "elevation": math.degrees(elevation),
                "azimuth": (math.degrees(azimuth) + 180) % 360,
            }

        except Exception as e:
            _LOGGER.error("Error calculating solar position: %s", e)
            return {"elevation": 0, "azimuth": 0}

    def calculate_panel_irradiance(
        solar_elevation: float,
        solar_azimuth: float,
        panel_tilt: float,
        panel_orientation: float,
    ) -> float:
        """Calculate irradiance on tilted panel."""
        try:
            if solar_elevation <= 0:
                return 0

            # Convert to radians
            sun_elev_rad = math.radians(solar_elevation)
            sun_azim_rad = math.radians(solar_azimuth)
            panel_tilt_rad = math.radians(panel_tilt)
            panel_azim_rad = math.radians(panel_orientation)

            # Calculate incidence angle
            cos_incidence = math.sin(sun_elev_rad) * math.cos(
                panel_tilt_rad
            ) + math.cos(sun_elev_rad) * math.sin(panel_tilt_rad) * math.cos(
                sun_azim_rad - panel_azim_rad
            )

            # Avoid negative values
            cos_incidence = max(0, cos_incidence)

            # Direct normal irradiance (simplified model)
            # Assume clear sky conditions
            air_mass = (
                1 / math.sin(sun_elev_rad) if solar_elevation > 0 else float("inf")
            )
            if air_mass > 10:
                dni = 0
            else:
                dni = 900 * math.exp(-0.14 * air_mass)  # Simplified clear sky model

            # Irradiance on tilted surface
            irradiance = dni * cos_incidence

            return max(0, irradiance)

        except Exception as e:
            _LOGGER.error("Error calculating panel irradiance: %s", e)
            return 0

    return calculate_solar_position, calculate_panel_irradiance


def test_solar_forecast():
    """Test the solar forecast calculation and print results."""

    print("=" * 60)
    print("🌞 SOLAR ENERGY FORECAST TEST")
    print("=" * 60)

    # Configuration (using values from your Home Assistant screenshot)
    latitude = 45.76  # Romania
    longitude = 21.42  # Romania
    timezone_str = "Europe/Bucharest"
    panel_tilt = 30.0  # degrees
    panel_orientation = 180.0  # South-facing
    pv_max_power = 10.0  # kW

    print(f"📍 Location: {latitude}°N, {longitude}°E")
    print(f"🕐 Timezone: {timezone_str}")
    print(f"📐 Panel Tilt: {panel_tilt}°")
    print(f"🧭 Panel Orientation: {panel_orientation}° (South)")
    print(f"⚡ PV Max Power: {pv_max_power} kW")
    print()

    # Get mock functions
    get_sun_times = mock_astral_functions()
    calculate_solar_position, calculate_panel_irradiance = mock_solar_calculations()

    # Implement the forecast calculation (similar to sensor.py)
    def calculate_energy_forecast_test(
        latitude: float,
        longitude: float,
        timezone: str,
        panel_tilt: float,
        panel_orientation: float,
        pv_max_power: float,
        start_time: datetime = None,
    ) -> dict:
        """Calculate energy production forecast."""
        try:
            if start_time is None:
                start_time = datetime.now()

            # Make timezone-aware
            if start_time.tzinfo is None:
                try:
                    import pytz

                    tz = pytz.timezone(timezone)
                    start_time = tz.localize(start_time)
                except ImportError:
                    # Fallback for Europe/Bucharest (UTC+2)
                    from datetime import timezone as dt_timezone

                    tz_offset = dt_timezone(timedelta(hours=2))
                    start_time = start_time.replace(tzinfo=tz_offset)

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
                print("🌙 Past sunset, calculating forecast for tomorrow")
                tomorrow = today + timedelta(days=1)
                tomorrow_sun_times = get_sun_times(
                    latitude, longitude, timezone, tomorrow
                )

                if (
                    tomorrow_sun_times
                    and "sunrise" in tomorrow_sun_times
                    and "sunset" in tomorrow_sun_times
                ):
                    sunrise_time = tomorrow_sun_times["sunrise"]
                    sunset_time = tomorrow_sun_times["sunset"]
                    forecast_day = tomorrow
                    print(
                        f"Using tomorrow's times: sunrise={sunrise_time}, sunset={sunset_time}"
                    )
                else:
                    print("Could not calculate tomorrow's sun times, using today's")
                    forecast_day = today
            else:
                print("🌅 Before sunset, using today's forecast")
                forecast_day = today

            # Calculate full day forecast (24 hours in 5-minute intervals = 288 intervals)
            full_day_forecast = []
            total_daily_energy = 0
            
            # Start from midnight of the forecast day
            if hasattr(forecast_day, 'date'):
                forecast_day_start = datetime.combine(forecast_day.date(), datetime.min.time())
            else:
                forecast_day_start = datetime.combine(forecast_day, datetime.min.time())
            
            # Make timezone-aware
            try:
                import pytz
                tz = pytz.timezone(timezone)
                current_time_full = tz.localize(forecast_day_start)
            except ImportError:
                current_time_full = forecast_day_start.replace(tzinfo=datetime.timezone.utc)

            print(
                f"Calculating forecast from {current_time_full} for {forecast_day} (24h = 288 intervals)"
            )

            # Generate 288 intervals (24 hours * 12 intervals per hour)
            for interval in range(288):
                # Get solar position
                solar_pos = calculate_solar_position(
                    latitude, longitude, current_time_full
                )

                # Calculate panel irradiance
                irradiance = calculate_panel_irradiance(
                    solar_pos["elevation"],
                    solar_pos["azimuth"],
                    panel_tilt,
                    panel_orientation,
                )

                # Calculate power output - pv_max_power is already the rated power
                if solar_pos["elevation"] > 0 and irradiance > 0:
                    # Standard Test Conditions: 1000 W/m²
                    # Power scales linearly with irradiance
                    power_kw = pv_max_power * (irradiance / 1000.0)
                    power_kw = max(0, min(power_kw, pv_max_power))  # Cap at max power
                else:
                    power_kw = 0.0

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

                if power_kw > 0:  # Only add energy during daylight
                    total_daily_energy += energy_5min
                
                current_time_full += timedelta(minutes=5)

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

            # Calculate remaining forecast (from now until sunset)
            forecast = []
            total_energy = 0

            # Get today's original sunset for comparison
            today_sun_times = get_sun_times(
                latitude, longitude, timezone, start_time.date()
            )
            original_sunset = (
                today_sun_times.get("sunset") if today_sun_times else sunset_time
            )

            if start_time < original_sunset:
                current_time = start_time
                while current_time < sunset_time:
                    solar_pos = calculate_solar_position(
                        latitude, longitude, current_time
                    )

                    if solar_pos["elevation"] > 0:
                        irradiance = calculate_panel_irradiance(
                            solar_pos["elevation"],
                            solar_pos["azimuth"],
                            panel_tilt,
                            panel_orientation,
                        )

                        # Calculate power output - pv_max_power is already the rated power
                        if irradiance > 0:
                            power_kw = pv_max_power * (irradiance / 1000.0)
                            power_kw = max(0, min(power_kw, pv_max_power))
                        else:
                            power_kw = 0.0

                        energy_5min = power_kw * (5 / 60)

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
                "forecast_day": forecast_day.isoformat(),
            }

        except Exception as e:
            print(f"❌ Error calculating energy forecast: {e}")
            import traceback

            traceback.print_exc()
            return {
                "total_energy": 0,
                "forecast": [],
                "full_day_forecast": [],
                "total_daily_energy": 0,
            }

    # Run the forecast calculation
    print("🔄 Calculating solar energy forecast...")
    forecast_data = calculate_energy_forecast_test(
        latitude=latitude,
        longitude=longitude,
        timezone=timezone_str,
        panel_tilt=panel_tilt,
        panel_orientation=panel_orientation,
        pv_max_power=pv_max_power,
    )

    # Print results
    print("\n" + "=" * 60)
    print("📊 FORECAST RESULTS")
    print("=" * 60)

    print(f"🔋 Total Energy Until Sunset: {forecast_data.get('total_energy', 0)} kWh")
    print(f"☀️ Total Daily Energy: {forecast_data.get('total_daily_energy', 0)} kWh")
    print(f"⏰ Forecast Start: {forecast_data.get('forecast_start', 'N/A')}")
    print(f"🌅 Sunrise: {forecast_data.get('sunrise_time', 'N/A')}")
    print(f"🌇 Sunset: {forecast_data.get('sunset_time', 'N/A')}")
    print(f"📅 Forecast Day: {forecast_data.get('forecast_day', 'N/A')}")
    print(f"📈 Remaining Intervals: {len(forecast_data.get('forecast', []))}")
    print(f"📊 Full Day Intervals: {len(forecast_data.get('full_day_forecast', []))}")

    # Show sample intervals
    full_day_forecast = forecast_data.get("full_day_forecast", [])
    if full_day_forecast:
        print(f"\n📋 SAMPLE FULL DAY FORECAST (first 10 intervals):")
        print(f"{'Time':<20} {'Elevation':<10} {'Power':<8} {'Energy':<10}")
        print("-" * 50)
        for i, entry in enumerate(full_day_forecast[:10]):
            time_str = entry["time"].split("T")[1][:5]  # Extract HH:MM
            print(
                f"{time_str:<20} {entry['solar_elevation']:<10.1f} {entry['power_kw']:<8.3f} {entry['energy_5min_kwh']:<10.4f}"
            )

        if len(full_day_forecast) > 10:
            print(f"... and {len(full_day_forecast) - 10} more intervals")

    # Show remaining forecast if available
    remaining_forecast = forecast_data.get("forecast", [])
    if remaining_forecast:
        print(f"\n⏳ REMAINING FORECAST (first 5 intervals):")
        print(f"{'Time':<20} {'Elevation':<10} {'Power':<8} {'Energy':<10}")
        print("-" * 50)
        for i, entry in enumerate(remaining_forecast[:5]):
            time_str = entry["time"].split("T")[1][:5]  # Extract HH:MM
            print(
                f"{time_str:<20} {entry['solar_elevation']:<10.1f} {entry['power_kw']:<8.3f} {entry['energy_5min_kwh']:<10.4f}"
            )

        if len(remaining_forecast) > 5:
            print(f"... and {len(remaining_forecast) - 5} more intervals")
    else:
        print(f"\n⏳ No remaining forecast (past sunset or no sun)")

    # Summary statistics
    if full_day_forecast:
        max_power = max(entry["power_kw"] for entry in full_day_forecast)
        max_power_entry = max(full_day_forecast, key=lambda x: x["power_kw"])
        max_time = max_power_entry["time"].split("T")[1][:5]

        print(f"\n📈 STATISTICS:")
        print(f"Peak Power: {max_power:.3f} kW at {max_time}")
        print(
            f"Average Power: {forecast_data.get('total_daily_energy', 0) * 12 / len(full_day_forecast):.3f} kW"
        )
        print(
            f"Forecast Efficiency: {(forecast_data.get('total_daily_energy', 0) / (pv_max_power * 10)) * 100:.1f}% of theoretical max"
        )

    print("\n" + "=" * 60)
    print("✅ FORECAST CALCULATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_solar_forecast()
