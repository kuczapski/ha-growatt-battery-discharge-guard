#!/usr/bin/env python3
"""Test the forecast function with timezone fix."""

import sys
import os
from datetime import datetime, timezone, timedelta

def test_forecast_with_timezone():
    """Test forecast calculation with proper timezone handling."""
    print("=== Testing Forecast with Timezone Fix ===")
    
    # Mock the necessary imports and functions
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'battery_management'))
    
    # Romania coordinates
    latitude = 45.76
    longitude = 21.42
    timezone_str = "Europe/Bucharest"
    
    print(f"Location: {latitude}°N, {longitude}°E")
    print(f"Timezone: {timezone_str}")
    
    # Test with current time (nighttime)
    now = datetime.now()
    print(f"Current time: {now}")
    
    # Simple test of our timezone logic
    if now.tzinfo is None:
        try:
            import pytz
            tz = pytz.timezone(timezone_str)
            now_aware = tz.localize(now)
            print(f"Made timezone-aware: {now_aware}")
        except ImportError:
            print("pytz not available, using fallback")
            # Bucharest is UTC+2
            tz_offset = timezone(timedelta(hours=2))
            now_aware = now.replace(tzinfo=tz_offset)
            print(f"Made timezone-aware (fallback): {now_aware}")
    
    # Test astral library sun times
    try:
        from astral import LocationInfo
        from astral.sun import sun
        
        location = LocationInfo("Test", "Romania", timezone_str, latitude, longitude)
        today = now.date()
        tomorrow = today + timedelta(days=1)
        
        sun_times_today = sun(location.observer, date=today)
        sun_times_tomorrow = sun(location.observer, date=tomorrow)
        
        print(f"\nToday's sunset: {sun_times_today['sunset']}")
        print(f"Tomorrow's sunrise: {sun_times_tomorrow['sunrise']}")
        print(f"Tomorrow's sunset: {sun_times_tomorrow['sunset']}")
        
        # Test comparison
        sunset_today = sun_times_today['sunset']
        if now_aware >= sunset_today:
            print("✓ Past today's sunset - should show tomorrow's forecast")
        else:
            print("⚠️ Before today's sunset - should show remaining forecast")
            
        # Calculate intervals for tomorrow
        sunrise_tomorrow = sun_times_tomorrow['sunrise']
        sunset_tomorrow = sun_times_tomorrow['sunset']
        
        intervals = 0
        current_time = sunrise_tomorrow
        while current_time < sunset_tomorrow:
            intervals += 1
            current_time += timedelta(minutes=5)
        
        print(f"\nTomorrow's forecast should have ~{intervals} intervals")
        
    except Exception as e:
        print(f"Error testing astral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_forecast_with_timezone()