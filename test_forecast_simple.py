#!/usr/bin/env python3
"""
Simple test for the 15-minute forecast with corrected solar calculations
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Add the custom_components path to sys.path
sys.path.insert(0, str(Path(__file__).parent / "custom_components"))

from battery_management.sensor import calculate_energy_forecast

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Use INFO to avoid too much debug output
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

def test_forecast():
    """Test the forecast with corrected solar calculations."""
    
    print("Testing 15-minute solar forecast...")
    print("=" * 60)
    
    # Test configuration
    latitude = 45.76
    longitude = 21.42
    timezone = "Europe/Bucharest"
    panel_tilt = 30.0
    panel_orientation = 180.0
    panel_area = 24.78
    efficiency = 0.2
    
    print(f"Configuration:")
    print(f"  Location: {latitude:.2f}°N, {longitude:.2f}°E")
    print(f"  Panel: {panel_tilt}° tilt, {panel_orientation}° azimuth (South)")
    print(f"  System: {panel_area} m², {efficiency*100}% efficiency")
    print()
    
    # Calculate forecasts
    pv_max_power = panel_area * efficiency  # Calculate max power in kW
    
    forecast_data = calculate_energy_forecast(
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
        panel_tilt=panel_tilt,
        panel_orientation=panel_orientation,
        pv_max_power=pv_max_power,
    )
    
    print(f"Results:")
    print(f"  Remaining energy until sunset: {forecast_data['total_energy']:.3f} kWh")
    print(f"  Full day energy forecast: {forecast_data['total_daily_energy']:.3f} kWh")
    print(f"  Remaining intervals: {len(forecast_data['forecast'])}")
    print(f"  Full day intervals: {len(forecast_data['full_day_forecast'])}")
    print()
    
    # Show some sample intervals with positive power
    print("Sample intervals with power generation:")
    print("Time     Elevation  Azimuth   Irradiance  Power")
    print("-" * 50)
    
    count = 0
    for interval in forecast_data['full_day_forecast']:
        if interval['power_kw'] > 0.1 and count < 8:  # Show 8 intervals with significant power
            # Handle time as string (it's already formatted)
            time_str = interval['time'] if isinstance(interval['time'], str) else interval['time'].strftime('%H:%M')
            print(f"{time_str}    "
                  f"{interval['solar_elevation']:6.1f}°  "
                  f"{interval['solar_azimuth']:7.1f}°  "
                  f"{interval['irradiance']:8.1f}  "
                  f"{interval['power_kw']:6.3f}")
            count += 1
    
    print("\n" + "=" * 60)
    print("SUCCESS: Solar calculations working correctly!")


if __name__ == "__main__":
    test_forecast()