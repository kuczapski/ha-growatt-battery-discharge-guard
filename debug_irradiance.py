#!/usr/bin/env python3
"""
Simple test to debug the irradiance calculation
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Add the custom_components path to sys.path
sys.path.insert(0, str(Path(__file__).parent / "custom_components"))

from battery_management.sensor import (
    calculate_panel_irradiance,
    calculate_solar_position,
)

# Configure logging to see debug output
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

# Explicitly set the battery_management logger to DEBUG level
logger = logging.getLogger("battery_management.sensor")
logger.setLevel(logging.DEBUG)


def test_irradiance():
    """Test irradiance calculation for a specific time."""

    print("Testing irradiance calculation...")
    print("=" * 50)

    # Test configuration
    latitude = 45.76
    longitude = 21.42
    timezone = "Europe/Bucharest"
    panel_tilt = 30.0
    panel_orientation = 180.0  # South-facing
    panel_area = 24.78
    efficiency = 0.2

    # Test for multiple times to see the pattern
    test_times = [
        datetime.now().replace(hour=8, minute=0, second=0, microsecond=0),
        datetime.now().replace(hour=10, minute=0, second=0, microsecond=0),
        datetime.now().replace(hour=12, minute=0, second=0, microsecond=0),
        datetime.now().replace(hour=14, minute=0, second=0, microsecond=0),
        datetime.now().replace(hour=16, minute=0, second=0, microsecond=0),
    ]

    print(f"Latitude: {latitude}, Longitude: {longitude}")
    print(
        f"Panel tilt: {panel_tilt}°, Orientation: {panel_orientation}° (South-facing)"
    )
    print()

    for test_time in test_times:
        print(f"\nTest time: {test_time.strftime('%H:%M')}")

        # First get solar position
        solar_data = calculate_solar_position(latitude, longitude, test_time)
        elevation = solar_data.get("elevation", 0)
        azimuth = solar_data.get("azimuth", 0)
        print(
            f"  Solar position - Elevation: {elevation:.1f}°, Azimuth: {azimuth:.1f}°"
        )

        # Then calculate irradiance
        irradiance = calculate_panel_irradiance(
            elevation, azimuth, panel_tilt, panel_orientation
        )

        print(f"  Calculated irradiance: {irradiance:.1f} W/m²")

        # Calculate power
        power = irradiance * panel_area * efficiency / 1000  # Convert to kW
        print(f"  Calculated power: {power:.3f} kW")

    print("\n" + "=" * 50)
    print("Check debug logs above for detailed calculation steps")


if __name__ == "__main__":
    test_irradiance()
