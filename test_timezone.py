#!/usr/bin/env python3
"""Test to debug the sun times and timezone issues."""

import sys
import os
from datetime import datetime, timedelta
import pytz

def test_timezone_awareness():
    """Test timezone handling for sun times."""
    print("=== Timezone Debug Test ===")
    
    # Romania coordinates from the screenshot
    latitude = 45.76
    longitude = 21.42
    timezone_str = "Europe/Bucharest"
    
    print(f"Location: {latitude}°N, {longitude}°E")
    print(f"Timezone: {timezone_str}")
    
    # Current time
    now = datetime.now()
    now_tz = datetime.now(pytz.timezone(timezone_str))
    
    print(f"\nCurrent time (naive): {now}")
    print(f"Current time (timezone-aware): {now_tz}")
    print(f"Is now timezone-aware: {now.tzinfo is not None}")
    print(f"Is now_tz timezone-aware: {now_tz.tzinfo is not None}")
    
    # Test astral library
    try:
        from astral import LocationInfo
        from astral.sun import sun
        
        print(f"\n=== Astral Library Test ===")
        location = LocationInfo("Test", "Romania", timezone_str, latitude, longitude)
        today = now.date()
        sun_times = sun(location.observer, date=today)
        
        print(f"Today's sun times:")
        for key, value in sun_times.items():
            print(f"  {key}: {value} (timezone-aware: {value.tzinfo is not None})")
        
        # Test comparison
        sunset = sun_times.get('sunset')
        if sunset:
            print(f"\nComparison test:")
            print(f"now >= sunset: {now >= sunset}")
            print(f"now_tz >= sunset: {now_tz >= sunset}")
            
            # Make timezone-aware comparison
            if now.tzinfo is None and sunset.tzinfo is not None:
                now_aware = pytz.timezone(timezone_str).localize(now)
                print(f"now_aware >= sunset: {now_aware >= sunset}")
        
        # Test tomorrow
        tomorrow = today + timedelta(days=1)
        tomorrow_sun_times = sun(location.observer, date=tomorrow)
        print(f"\nTomorrow's sun times:")
        for key, value in tomorrow_sun_times.items():
            print(f"  {key}: {value}")
            
    except ImportError as e:
        print(f"Astral library not available: {e}")
    except Exception as e:
        print(f"Error testing astral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_timezone_awareness()