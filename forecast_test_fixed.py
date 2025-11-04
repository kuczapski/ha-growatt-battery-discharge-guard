#!/usr/bin/env python3
"""
Comprehensive Solar Energy Forecast Test
This script tests the solar energy forecast calculation with realistic values
"""

import math
from datetime import datetime, timedelta, timezone as dt_timezone
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


def calculate_solar_position(latitude: float, longitude: float, dt: datetime) -> dict:
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
        declination = 23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365))

        # Hour angle from solar noon (degrees)
        # Adjust for longitude and timezone
        time_of_day = dt_local.hour + dt_local.minute / 60.0 + dt_local.second / 3600.0
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
    elevation: float, azimuth: float, panel_tilt: float, panel_orientation: float
) -> float:
    """Calculate solar irradiance on tilted panel."""
    if elevation <= 0:
        return 0

    # Convert to radians
    elev_rad = math.radians(elevation)
    azim_rad = math.radians(azimuth)
    tilt_rad = math.radians(panel_tilt)
    orient_rad = math.radians(panel_orientation)

    # Angle between sun and panel normal
    cos_incidence = math.sin(elev_rad) * math.cos(tilt_rad) + math.cos(
        elev_rad
    ) * math.sin(tilt_rad) * math.cos(azim_rad - orient_rad)

    # Air mass calculation
    air_mass = 1 / math.sin(elev_rad) if elevation > 0 else float("inf")
    air_mass = min(air_mass, 10)  # Cap at 10

    # Clear sky irradiance (simplified model)
    dni = 900.0 * math.exp(-0.14 * air_mass)  # Direct normal irradiance

    # Panel irradiance
    panel_irradiance = max(0, dni * cos_incidence)

    return panel_irradiance


def get_sun_times(latitude: float, longitude: float, timezone: str, date_obj):
    """Mock function to get sunrise and sunset times."""
    try:
        from astral import LocationInfo
        from astral.sun import sun

        location = LocationInfo("Test", "Test", timezone, latitude, longitude)
        s = sun(location.observer, date=date_obj)

        return {"sunrise": s["sunrise"], "sunset": s["sunset"]}
    except ImportError:
        # Fallback calculation
        base_date = datetime.combine(date_obj, datetime.min.time())
        base_date = base_date.replace(tzinfo=dt_timezone.utc)

        return {
            "sunrise": base_date + timedelta(hours=7),  # 7 AM UTC
            "sunset": base_date + timedelta(hours=16),  # 4 PM UTC
        }


def test_forecast():
    """Test the solar energy forecast calculation."""

    # Configuration
    LATITUDE = 45.76
    LONGITUDE = 21.42
    TIMEZONE = "Europe/Bucharest"
    PANEL_TILT = 30.0
    PANEL_ORIENTATION = 180.0  # South
    PV_MAX_POWER = 10.0  # kW

    print("=" * 60)
    print("🌞 SOLAR ENERGY FORECAST TEST")
    print("=" * 60)
    print(f"📍 Location: {LATITUDE}°N, {LONGITUDE}°E")
    print(f"🕐 Timezone: {TIMEZONE}")
    print(f"📐 Panel Tilt: {PANEL_TILT}°")
    print(f"🧭 Panel Orientation: {PANEL_ORIENTATION}° (South)")
    print(f"⚡ PV Max Power: {PV_MAX_POWER} kW")
    print()
    print("🔄 Calculating solar energy forecast...")

    # Use current time as start time
    start_time = datetime.now(dt_timezone.utc)
    today = start_time.date()

    # Get sun times
    sun_times = get_sun_times(LATITUDE, LONGITUDE, TIMEZONE, today)
    sunrise_time = sun_times["sunrise"]
    sunset_time = sun_times["sunset"]

    # Check if we're past sunset
    forecast_day = today
    if start_time >= sunset_time:
        print("🌙 Past sunset, calculating forecast for tomorrow")
        tomorrow = today + timedelta(days=1)
        tomorrow_sun_times = get_sun_times(LATITUDE, LONGITUDE, TIMEZONE, tomorrow)
        sunrise_time = tomorrow_sun_times["sunrise"]
        sunset_time = tomorrow_sun_times["sunset"]
        forecast_day = tomorrow
        print(f"Using tomorrow's times: sunrise={sunrise_time}, sunset={sunset_time}")

    # Calculate full day forecast (24 hours in 5-minute intervals = 288 intervals)
    full_day_forecast = []
    total_daily_energy = 0

    # Start from midnight of the forecast day
    if hasattr(forecast_day, "date"):
        forecast_day_start = datetime.combine(forecast_day.date(), datetime.min.time())
    else:
        forecast_day_start = datetime.combine(forecast_day, datetime.min.time())

    # Make timezone-aware
    try:
        import pytz

        tz = pytz.timezone(TIMEZONE)
        current_time_full = tz.localize(forecast_day_start)
    except ImportError:
        current_time_full = forecast_day_start.replace(tzinfo=dt_timezone.utc)

    print(
        f"Calculating forecast from {current_time_full} for {forecast_day} (24h = 288 intervals)"
    )

    # Generate 288 intervals (24 hours * 12 intervals per hour)
    for interval in range(288):
        # Get solar position
        solar_pos = calculate_solar_position(LATITUDE, LONGITUDE, current_time_full)

        # Calculate panel irradiance
        irradiance = calculate_panel_irradiance(
            solar_pos["elevation"],
            solar_pos["azimuth"],
            PANEL_TILT,
            PANEL_ORIENTATION,
        )

        # Calculate power output - pv_max_power is already the rated power
        if solar_pos["elevation"] > 0 and irradiance > 0:
            # Standard Test Conditions: 1000 W/m²
            # Power scales linearly with irradiance
            power_kw = PV_MAX_POWER * (irradiance / 1000.0)
            power_kw = max(0, min(power_kw, PV_MAX_POWER))  # Cap at max power
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

    # Calculate remaining forecast (if before sunset)
    remaining_forecast = []
    remaining_energy = 0

    if start_time < sunset_time:
        current_time = start_time
        while current_time < sunset_time:
            solar_pos = calculate_solar_position(LATITUDE, LONGITUDE, current_time)

            if solar_pos["elevation"] > 0:
                irradiance = calculate_panel_irradiance(
                    solar_pos["elevation"],
                    solar_pos["azimuth"],
                    PANEL_TILT,
                    PANEL_ORIENTATION,
                )

                if irradiance > 0:
                    power_kw = PV_MAX_POWER * (irradiance / 1000.0)
                    power_kw = max(0, min(power_kw, PV_MAX_POWER))
                else:
                    power_kw = 0.0

                energy_5min = power_kw * (5 / 60)

                remaining_forecast.append(
                    {
                        "time": current_time.isoformat(),
                        "solar_elevation": round(solar_pos["elevation"], 2),
                        "power_kw": round(power_kw, 3),
                        "energy_5min_kwh": round(energy_5min, 4),
                    }
                )

                remaining_energy += energy_5min

            current_time += timedelta(minutes=5)

    # Print results
    print("=" * 60)
    print("📊 FORECAST RESULTS")
    print("=" * 60)
    print(f"🔋 Total Energy Until Sunset: {remaining_energy:.3f} kWh")
    print(f"☀️ Total Daily Energy: {total_daily_energy:.3f} kWh")
    print(f"⏰ Forecast Start: {start_time.isoformat()}")
    print(f"🌅 Sunrise: {sunrise_time}")
    print(f"🌇 Sunset: {sunset_time}")
    print(f"📅 Forecast Day: {forecast_day}")
    print(f"📈 Remaining Intervals: {len(remaining_forecast)}")
    print(f"📊 Full Day Intervals: {len(full_day_forecast)}")
    print()

    # Show sample forecast
    print("📋 SAMPLE FULL DAY FORECAST (first 10 intervals):")
    print("Time                 Elevation  Power    Energy")
    print("-" * 50)
    for i, item in enumerate(full_day_forecast[:10]):
        time_str = datetime.fromisoformat(item["time"]).strftime("%H:%M")
        print(
            f"{time_str:<20} {item['solar_elevation']:<10.1f} {item['power_kw']:<8.3f} {item['energy_5min_kwh']:<8.4f}"
        )

    if len(full_day_forecast) > 10:
        print(f"... and {len(full_day_forecast) - 10} more intervals")
    print()

    if remaining_forecast:
        print("⏳ REMAINING FORECAST (next 5 intervals):")
        print("Time                 Elevation  Power    Energy")
        print("-" * 50)
        for item in remaining_forecast[:5]:
            time_str = datetime.fromisoformat(item["time"]).strftime("%H:%M")
            print(
                f"{time_str:<20} {item['solar_elevation']:<10.1f} {item['power_kw']:<8.3f} {item['energy_5min_kwh']:<8.4f}"
            )
    else:
        print("⏳ No remaining forecast (past sunset or no sun)")

    # Calculate statistics
    powers = [item["power_kw"] for item in full_day_forecast if item["power_kw"] > 0]
    if powers:
        peak_power = max(powers)
        avg_power = sum(powers) / len(powers)
        peak_item = max(full_day_forecast, key=lambda x: x["power_kw"])
        peak_time = datetime.fromisoformat(peak_item["time"]).strftime("%H:%M")

        print()
        print("📈 STATISTICS:")
        print(f"Peak Power: {peak_power:.3f} kW at {peak_time}")
        print(f"Average Power: {avg_power:.3f} kW")
        print(
            f"Forecast Efficiency: {(total_daily_energy / (PV_MAX_POWER * 12)) * 100:.1f}% of theoretical max"
        )

    print()
    print("=" * 60)
    print("✅ FORECAST CALCULATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_forecast()
