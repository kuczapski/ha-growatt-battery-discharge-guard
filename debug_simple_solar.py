#!/usr/bin/env python3
"""
Simple debug test for solar calculations.
"""

from datetime import datetime, timedelta
import math


def test_simple_solar():
    """Test basic solar calculations for Romania at different times."""
    print("=== Simple Solar Position Test ===")

    latitude = 45.76  # Romania
    longitude = 21.42  # Romania

    # Test different times tomorrow
    tomorrow = datetime.now().date() + timedelta(days=1)

    test_times = [
        8,  # 8 AM
        10,  # 10 AM
        12,  # Noon
        14,  # 2 PM
        16,  # 4 PM
    ]

    for hour in test_times:
        test_dt = datetime.combine(tomorrow, datetime.min.time().replace(hour=hour))

        # Simple solar position calculation
        def calculate_solar_position_simple(lat, lon, dt):
            # Day of year
            day_of_year = dt.timetuple().tm_yday

            # Solar declination
            declination = 23.45 * math.sin(
                math.radians(360 * (284 + day_of_year) / 365)
            )

            # Hour angle (simplified - assumes local solar time)
            hour_angle = 15 * (dt.hour - 12)  # degrees from solar noon

            # Convert to radians
            lat_rad = math.radians(lat)
            dec_rad = math.radians(declination)
            hour_rad = math.radians(hour_angle)

            # Solar elevation
            elevation = math.asin(
                math.sin(lat_rad) * math.sin(dec_rad)
                + math.cos(lat_rad) * math.cos(dec_rad) * math.cos(hour_rad)
            )

            # Solar azimuth (simplified)
            azimuth = math.atan2(
                math.sin(hour_rad),
                math.cos(hour_rad) * math.sin(lat_rad)
                - math.tan(dec_rad) * math.cos(lat_rad),
            )

            return {
                "elevation": math.degrees(elevation),
                "azimuth": (math.degrees(azimuth) + 180) % 360,
            }

        solar_pos = calculate_solar_position_simple(latitude, longitude, test_dt)

        print(
            f"{hour:2d}:00 - Elevation: {solar_pos['elevation']:6.2f}°, Azimuth: {solar_pos['azimuth']:6.2f}°"
        )

        # Test panel irradiance
        if solar_pos["elevation"] > 0:
            # Simple irradiance calculation
            # Direct normal irradiance (clear sky model)
            air_mass = 1 / math.sin(math.radians(solar_pos["elevation"]))
            if air_mass <= 10:
                dni = 900 * math.exp(-0.14 * air_mass)

                # Panel calculations (30° tilt, south-facing)
                panel_tilt = 30.0
                panel_azimuth = 180.0

                # Incidence angle on tilted panel
                sun_elev_rad = math.radians(solar_pos["elevation"])
                sun_azim_rad = math.radians(solar_pos["azimuth"])
                panel_tilt_rad = math.radians(panel_tilt)
                panel_azim_rad = math.radians(panel_azimuth)

                cos_incidence = math.sin(sun_elev_rad) * math.cos(
                    panel_tilt_rad
                ) + math.cos(sun_elev_rad) * math.sin(panel_tilt_rad) * math.cos(
                    sun_azim_rad - panel_azim_rad
                )

                cos_incidence = max(0, cos_incidence)
                irradiance = dni * cos_incidence

                # Power calculation
                pv_max_power = 10.0  # kW
                panel_efficiency = 0.20
                system_efficiency = 0.90

                power_kw = (
                    (irradiance / 1000)
                    * pv_max_power
                    * panel_efficiency
                    * system_efficiency
                )

                print(
                    f"      DNI: {dni:6.2f} W/m², Panel Irradiance: {irradiance:6.2f} W/m², Power: {power_kw:6.3f} kW"
                )
            else:
                print(f"      Air mass too high: {air_mass:.2f}")
        else:
            print(f"      Sun below horizon")

    print("\n=== Using Astral Library ===")
    try:
        from astral import LocationInfo
        from astral.sun import sun
        from astral.sun import elevation as astral_elevation

        location = LocationInfo(
            "Romania", "Romania", "Europe/Bucharest", latitude, longitude
        )
        sun_times = sun(location.observer, date=tomorrow)

        print(f"Sunrise: {sun_times['sunrise']}")
        print(f"Sunset:  {sun_times['sunset']}")

        # Test elevation at noon
        noon_tomorrow = datetime.combine(
            tomorrow,
            datetime.min.time().replace(hour=12, tzinfo=sun_times["sunrise"].tzinfo),
        )
        noon_elevation = astral_elevation(location.observer, noon_tomorrow)

        print(f"Elevation at noon: {noon_elevation:.2f}°")

    except ImportError:
        print("Astral library not available")
    except Exception as e:
        print(f"Error with astral: {e}")


if __name__ == "__main__":
    test_simple_solar()
