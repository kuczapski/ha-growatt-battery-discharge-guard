#!/usr/bin/env python3
"""
Test script for 15-minute interval solar energy forecast with detailed logging
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Add the custom_components path to sys.path
sys.path.insert(0, str(Path(__file__).parent / "custom_components"))

from battery_management.sensor import calculate_energy_forecast

# Configure logging to see the output
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG to see detailed interval logs
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

# Explicitly set the battery_management logger to DEBUG level to see irradiance debug logs
logger = logging.getLogger("battery_management.sensor")
logger.setLevel(logging.DEBUG)


def test_15min_forecast():
    """Test the 15-minute interval forecast with detailed logging."""

    print("=" * 80)
    print("🌞 TESTING 15-MINUTE SOLAR FORECAST WITH DETAILED LOGGING")
    print("=" * 80)
    print()
    print("This test demonstrates:")
    print("  📊 15-minute intervals (96 intervals per day)")
    print("  🔍 Detailed logging for each calculation")
    print("  ⚡ Irradiance and power values for each interval")
    print()
    print("Log levels:")
    print("  📊 INFO: Main calculation steps and results")
    print("  🔍 DEBUG: Individual interval calculations")
    print("  ❌ ERROR: Error conditions")
    print()
    print("=" * 80)
    print()

    # Test configuration
    latitude = 45.76
    longitude = 21.42
    timezone = "Europe/Bucharest"
    panel_tilt = 30.0
    panel_orientation = 180.0
    pv_max_power = 10.0

    print(f"Testing with: {latitude}°N, {longitude}°E, {timezone}")
    print(
        f"Panel: {panel_tilt}° tilt, {panel_orientation}° orientation, {pv_max_power}kW max power"
    )
    print()
    print("🔴 Starting forecast calculation (watch for detailed logs)...")
    print("=" * 80)

    # Call the forecast function - this will generate the logs
    result = calculate_energy_forecast(
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
        panel_tilt=panel_tilt,
        panel_orientation=panel_orientation,
        pv_max_power=pv_max_power,
    )

    print("=" * 80)
    print("🔴 Forecast calculation complete!")
    print()
    print("📋 RESULTS SUMMARY:")
    print(f"  🔋 Remaining Energy: {result.get('total_energy', 0):.3f} kWh")
    print(f"  ☀️ Daily Energy: {result.get('total_daily_energy', 0):.3f} kWh")
    print(f"  📈 Remaining Intervals: {len(result.get('forecast', []))}")
    print(f"  📊 Full Day Intervals: {len(result.get('full_day_forecast', []))}")
    print()

    # Show sample forecast data
    forecast = result.get("forecast", [])
    if forecast:
        print("📋 SAMPLE REMAINING FORECAST (first 3 intervals):")
        print("Time     Elevation  Azimuth   Irradiance  Power    Energy")
        print("-" * 65)
        for i, item in enumerate(forecast[:3]):
            if "time" in item:
                time_str = datetime.fromisoformat(item["time"]).strftime("%H:%M")
                print(
                    f"{time_str:<8} {item.get('solar_elevation', 0):<9.1f}° {item.get('solar_azimuth', 0):<9.1f}° {item.get('irradiance', 0):<10.1f} {item.get('power_kw', 0):<8.3f} {item.get('energy_15min_kwh', 0):<8.4f}"
                )

    full_day = result.get("full_day_forecast", [])
    if full_day:
        print()
        print("📊 SAMPLE FULL DAY FORECAST (noon area):")
        print("Time     Elevation  Azimuth   Irradiance  Power    Energy")
        print("-" * 65)
        # Show intervals around noon (48th interval = 12:00)
        noon_start = max(0, 48 - 2)
        noon_end = min(len(full_day), 48 + 3)
        for i in range(noon_start, noon_end):
            item = full_day[i]
            if "time" in item:
                time_str = datetime.fromisoformat(item["time"]).strftime("%H:%M")
                print(
                    f"{time_str:<8} {item.get('solar_elevation', 0):<9.1f}° {item.get('solar_azimuth', 0):<9.1f}° {item.get('irradiance', 0):<10.1f} {item.get('power_kw', 0):<8.3f} {item.get('energy_15min_kwh', 0):<8.4f}"
                )

    print()
    print("=" * 80)
    print("✅ 15-MINUTE FORECAST TEST COMPLETE")
    print()
    print("Key changes from 5-minute intervals:")
    print("  • 96 intervals per day instead of 288")
    print("  • Each interval represents 15 minutes instead of 5")
    print("  • Energy values are per 15-minute period")
    print("  • More efficient calculation with same accuracy")
    print()
    print("In Home Assistant, you'll see detailed logs for each interval:")
    print("  • Solar elevation and azimuth angles")
    print("  • Panel irradiance values")
    print("  • Power output calculations")
    print("  • Energy values per 15-minute period")
    print("=" * 80)


if __name__ == "__main__":
    test_15min_forecast()
