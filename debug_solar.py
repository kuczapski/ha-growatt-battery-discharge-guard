#!/usr/bin/env python3
"""Debug script for solar energy forecast issues."""

from datetime import datetime, timedelta
import math


def test_basic_solar_calculation():
    """Test basic solar calculations to understand the issue."""
    print("=== Solar Forecast Debug Test ===")

    # Use the exact coordinates from the screenshot
    latitude = 45.76  # Romania
    longitude = 21.42  # Romania
    timezone = "Europe/Bucharest"

    # Current time (nighttime in screenshot)
    now = datetime.now()
    print(f"Current time: {now}")
    print(f"Location: {latitude}°N, {longitude}°E")
    print(f"Timezone: {timezone}")
    print()

    # Calculate Julian day number (simplified for testing)
    def julian_day(dt):
        a = (14 - dt.month) // 12
        y = dt.year + 4800 - a
        m = dt.month + 12 * a - 3
        jdn = (
            dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        )
        return jdn + (dt.hour - 12) / 24.0

    # Simple solar position calculation
    def calculate_sun_position(lat, lon, dt):
        jd = julian_day(dt)
        n = jd - 2451545.0

        # Mean solar longitude
        L = (280.460 + 0.9856474 * n) % 360

        # Mean solar anomaly
        g = math.radians((357.528 + 0.9856003 * n) % 360)

        # Ecliptic longitude
        lamb = math.radians(L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g))

        # Solar declination
        delta = math.asin(math.sin(math.radians(23.439)) * math.sin(lamb))

        # Hour angle
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)

        # Greenwich Mean Sidereal Time
        gmst = (18.697374558 + 24.06570982441908 * n) % 24

        # Local hour angle
        hour_angle = math.radians(15 * (gmst - dt.hour - lon / 15))

        # Solar elevation
        elevation = math.asin(
            math.sin(lat_rad) * math.sin(delta)
            + math.cos(lat_rad) * math.cos(delta) * math.cos(hour_angle)
        )

        # Solar azimuth
        azimuth = math.atan2(
            math.sin(hour_angle),
            math.cos(hour_angle) * math.sin(lat_rad)
            - math.tan(delta) * math.cos(lat_rad),
        )

        return {
            "elevation": math.degrees(elevation),
            "azimuth": (math.degrees(azimuth) + 180) % 360,
        }

    # Test current solar position
    position = calculate_sun_position(latitude, longitude, now)
    print(f"Current solar elevation: {position['elevation']:.2f}°")
    print(f"Current solar azimuth: {position['azimuth']:.2f}°")

    if position["elevation"] < 0:
        print("✓ Sun is below horizon (nighttime) - this explains 0 values")
    else:
        print("⚠️ Sun should be above horizon - check calculations")

    print()

    # Test tomorrow's forecast
    print("=== Testing Tomorrow's Forecast ===")
    tomorrow_6am = (now + timedelta(days=1)).replace(
        hour=6, minute=0, second=0, microsecond=0
    )
    tomorrow_noon = (now + timedelta(days=1)).replace(
        hour=12, minute=0, second=0, microsecond=0
    )

    pos_6am = calculate_sun_position(latitude, longitude, tomorrow_6am)
    pos_noon = calculate_sun_position(latitude, longitude, tomorrow_noon)

    print(
        f"Tomorrow 6 AM: elevation={pos_6am['elevation']:.2f}°, azimuth={pos_6am['azimuth']:.2f}°"
    )
    print(
        f"Tomorrow noon: elevation={pos_noon['elevation']:.2f}°, azimuth={pos_noon['azimuth']:.2f}°"
    )

    # Calculate approximate sunrise/sunset for tomorrow
    print("\n=== Approximate Sunrise/Sunset ===")
    for hour in range(0, 24):
        test_time = (now + timedelta(days=1)).replace(
            hour=hour, minute=0, second=0, microsecond=0
        )
        pos = calculate_sun_position(latitude, longitude, test_time)

        if hour > 0:
            prev_time = test_time - timedelta(hours=1)
            prev_pos = calculate_sun_position(latitude, longitude, prev_time)

            # Check for sunrise (elevation crosses 0 going up)
            if prev_pos["elevation"] < 0 and pos["elevation"] > 0:
                print(f"Approximate sunrise: {test_time.strftime('%H:%M')}")

            # Check for sunset (elevation crosses 0 going down)
            if prev_pos["elevation"] > 0 and pos["elevation"] < 0:
                print(f"Approximate sunset: {test_time.strftime('%H:%M')}")

    print("\n=== Conclusion ===")
    print("If you're seeing 0 values at night, this is CORRECT behavior.")
    print("The sensor should show tomorrow's forecast when it's past today's sunset.")
    print("Check if the forecast updates properly during daytime hours.")


if __name__ == "__main__":
    test_basic_solar_calculation()
