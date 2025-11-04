#!/usr/bin/env python3
"""
Test script to demonstrate the logging output from the solar energy forecast sensor
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
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)


def test_logging():
    """Test the logging output from the forecast calculation."""

    print("=" * 80)
    print("🔍 TESTING SOLAR ENERGY FORECAST LOGGING")
    print("=" * 80)
    print()
    print("This test demonstrates the logging that will appear in Home Assistant logs")
    print("when the Solar Energy Forecast sensor calculates its values.")
    print()
    print("Log levels:")
    print("  📊 INFO: Main calculation steps and results")
    print("  🔍 DEBUG: Detailed calculation progress")
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
    print("🔴 Starting forecast calculation (watch for logs)...")
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
    print("=" * 80)
    print("✅ LOGGING TEST COMPLETE")
    print()
    print("In Home Assistant, these logs will appear in:")
    print("  • Developer Tools > Logs")
    print("  • Configuration > Logs")
    print("  • home-assistant.log file")
    print()
    print("To see these logs in Home Assistant:")
    print("  1. Go to Developer Tools > Logs")
    print("  2. Filter by 'custom_components.battery_management'")
    print("  3. The sensor updates every 30 seconds by default")
    print("=" * 80)


if __name__ == "__main__":
    test_logging()
