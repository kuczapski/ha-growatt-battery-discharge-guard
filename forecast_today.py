#!/usr/bin/env python3
"""
Local test script for today's solar energy forecast
This script simulates the forecast for a daytime hour to show realistic values
"""

import math
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


class MockLocation:
    """Mock location for testing"""

    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude


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

    # Enhanced clear sky irradiance (balanced for realistic daily totals)
    # Maintain peak performance while reducing daily overestimation
    transmission = 0.78 ** (air_mass**0.62)  # Slightly more conservative
    dni = 1150.0 * transmission  # Reduced from 1200 to 1150

    # Enhanced empirical clear-sky global horizontal irradiance
    ghi = dni * math.sin(elev_rad) + 160.0  # Reduced base diffuse from 180 to 160
    diffuse = 0.25 * ghi  # Reduced diffuse component from 30% to 25%
    reflected = (
        0.25 * (1 - math.cos(tilt_rad)) * ghi / 2
    )  # Reduced albedo from 0.3 to 0.25

    panel_irradiance = max(0, dni * cos_incidence + diffuse + reflected)

    # Panel irradiance
    # Panel_irradiance = max(0, dni * cos_incidence)

    return panel_irradiance


def simulate_daytime_forecast():
    """Simulate a forecast during daytime hours"""

    # Configuration
    LATITUDE = 45.76
    LONGITUDE = 21.42
    PANEL_TILT = 30.0
    PANEL_ORIENTATION = 180.0  # South
    PV_MAX_POWER = 10.0  # kW

    print("=" * 60)
    print("🌞 DAYTIME SOLAR FORECAST SIMULATION")
    print("=" * 60)
    print(f"📍 Location: {LATITUDE}°N, {LONGITUDE}°E")
    print(f"📐 Panel Tilt: {PANEL_TILT}°")
    print(f"🧭 Panel Orientation: {PANEL_ORIENTATION}° (South)")
    print(f"⚡ PV Max Power: {PV_MAX_POWER} kW")
    print()

    # Simulate from 9 AM to 3 PM (peak hours)
    base_time = datetime(2025, 11, 4, 9, 0, 0)  # 9 AM

    total_energy = 0.0
    intervals = []

    print("📊 HOURLY FORECAST SIMULATION:")
    print("Time     Elevation  Azimuth   Irradiance  Power    Energy")
    print("-" * 60)

    for hour_offset in range(7):  # 9 AM to 3 PM (7 hours)
        current_time = base_time + timedelta(hours=hour_offset)

        # Calculate solar position
        solar_pos = calculate_solar_position(LATITUDE, LONGITUDE, current_time)
        elevation = solar_pos["elevation"]
        azimuth = solar_pos["azimuth"]

        # Calculate irradiance
        irradiance = calculate_panel_irradiance(
            elevation, azimuth, PANEL_TILT, PANEL_ORIENTATION
        )

        # Calculate power output
        if irradiance > 0:
            power = min(PV_MAX_POWER, PV_MAX_POWER * irradiance / 1000.0)
        else:
            power = 0.0

        # Energy for this hour (kWh)
        energy_hour = power  # 1 hour * power in kW = kWh
        total_energy += energy_hour

        intervals.append(
            {
                "time": current_time,
                "elevation": elevation,
                "azimuth": azimuth,
                "irradiance": irradiance,
                "power": power,
                "energy": energy_hour,
            }
        )

        print(
            f"{current_time.strftime('%H:%M')}    {elevation:6.1f}°   {azimuth:6.1f}°   {irradiance:8.1f}    {power:5.3f}    {energy_hour:6.3f}"
        )

    print("-" * 60)
    print(f"📈 Total Energy (9 AM - 3 PM): {total_energy:.3f} kWh")

    # Find peak hour
    peak_interval = max(intervals, key=lambda x: x["power"])
    print(
        f"🔥 Peak Power: {peak_interval['power']:.3f} kW at {peak_interval['time'].strftime('%H:%M')}"
    )
    print(f"☀️ Peak Elevation: {peak_interval['elevation']:.1f}°")

    print()
    print("✅ SIMULATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    simulate_daytime_forecast()
