#!/usr/bin/env python3
"""Quick test script for solar energy forecast functionality."""

import sys
import os

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "custom_components", "battery_management"),
)

from sensor import (
    calculate_energy_forecast,
    calculate_solar_position,
    calculate_panel_irradiance,
)
from datetime import datetime
import json


def test_solar_calculations():
    """Test the solar calculation functions."""
    print("Testing Solar Calculation Functions")
    print("=" * 40)

    # Test location (example: Berlin, Germany)
    latitude = 52.52
    longitude = 13.405
    timezone = "Europe/Berlin"

    # Panel configuration
    panel_tilt = 30.0  # 30 degrees
    panel_orientation = 180.0  # South-facing
    pv_max_power = 10.0  # 10 kW system

    print(f"Location: {latitude}°N, {longitude}°E")
    print(f"Timezone: {timezone}")
    print(f"Panel Tilt: {panel_tilt}°")
    print(f"Panel Orientation: {panel_orientation}° (South)")
    print(f"PV Max Power: {pv_max_power} kW")
    print()

    # Test solar position calculation
    print("Testing solar position calculation...")
    now = datetime.now()
    try:
        position = calculate_solar_position(latitude, longitude, now)
        print(f"Current time: {now}")
        print(f"Solar elevation: {position['elevation']:.2f}°")
        print(f"Solar azimuth: {position['azimuth']:.2f}°")
        print()
    except Exception as e:
        print(f"Error calculating solar position: {e}")
        print()

    # Test panel irradiance calculation
    print("Testing panel irradiance calculation...")
    try:
        if "position" in locals():
            irradiance = calculate_panel_irradiance(
                position["elevation"],
                position["azimuth"],
                panel_tilt,
                panel_orientation,
            )
            print(f"Panel irradiance: {irradiance:.2f} W/m²")
            print()
    except Exception as e:
        print(f"Error calculating panel irradiance: {e}")
        print()

    # Test energy forecast
    print("Testing energy forecast calculation...")
    try:
        forecast_data = calculate_energy_forecast(
            latitude=latitude,
            longitude=longitude,
            timezone=timezone,
            panel_tilt=panel_tilt,
            panel_orientation=panel_orientation,
            pv_max_power=pv_max_power,
        )

        print(
            f"Total expected energy until sunset: {forecast_data.get('total_energy', 0):.3f} kWh"
        )
        print(f"Number of forecast intervals: {len(forecast_data.get('forecast', []))}")

        if "sunset_time" in forecast_data:
            print(f"Sunset time: {forecast_data['sunset_time']}")

        if "forecast_start" in forecast_data:
            print(f"Forecast start: {forecast_data['forecast_start']}")

        # Show first few forecast entries
        forecast = forecast_data.get("forecast", [])
        if forecast:
            print("\nFirst 5 forecast intervals:")
            for i, entry in enumerate(forecast[:5]):
                print(
                    f"  {entry['time']}: {entry['power_kw']:.3f} kW, "
                    f"Solar elevation: {entry['solar_elevation']:.1f}°, "
                    f"Energy: {entry['energy_kwh']:.4f} kWh"
                )

        print(f"\nForecast calculation successful!")

    except Exception as e:
        print(f"Error calculating energy forecast: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_solar_calculations()
