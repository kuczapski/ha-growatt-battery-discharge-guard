# GROWATT Battery Discharge Guard for Home Assistant

A custom Home Assistant integration for monitoring and managing GROWATT battery systems with discharge protection features.

## Features

- 🔋 **Battery Level Monitoring**: Real-time battery level tracking from GROWATT servers
- ⚡ **Charging Status Detection**: Monitor charging state and power consumption
- 🛡️ **Discharge Protection**: Configurable low battery alerts and protection
- � **Solar Awareness**: Sunset time tracking for solar-aware battery management
- ⏰ **Time-based Optimization**: Countdown to sunset for energy planning
- �🎛️ **Configurable Thresholds**: Set custom low battery alerts and update intervals
- 🔄 **Auto-refresh**: Configurable update intervals for real-time monitoring
- 🎚️ **Battery Optimization**: Enable/disable power optimization modes

## Requirements

- Home Assistant 2023.1.0 or newer
- GROWATT account credentials (username and password)
- Active GROWATT solar/battery system

## Installation

### Manual Installation

1. Copy the `custom_components/battery_management` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to **Configuration** → **Integrations**
4. Click **Add Integration** and search for "Battery Management"

### HACS Installation (Recommended)

1. Add this repository to HACS as a custom repository
2. Install "Battery Management" from HACS
3. Restart Home Assistant
4. Add the integration through the UI

## Configuration

The integration can be configured through the Home Assistant UI:

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "GROWATT Battery Discharge Guard"
4. Configure with your GROWATT credentials and system parameters:
   - **Name**: Custom name for your battery management instance
   - **GROWATT Username**: Your GROWATT server username
   - **GROWATT Password**: Your GROWATT server password
   - **PV Installation Max Power (kW)**: Maximum power output of your solar panels
   - **Battery Capacity (kWh)**: Total capacity of your battery system
   - **Minimum discharge percentage (%)**: Minimum battery level for discharge protection
   - **Solar Panel Tilt Angle (°)**: Angle of your solar panels (0° = flat, 90° = vertical)
   - **Solar Panel Orientation (° from South)**: Panel direction (0° = South, 90° = West, 180° = North, 270° = East)
   - **Update Interval**: How often to check battery status (seconds)
   - **Low Battery Threshold**: Battery level percentage to trigger low battery alerts

## Entities

### Sensors

- `sensor.growatt_battery_discharge_guard_level`: Current battery level (%)
- `sensor.growatt_battery_discharge_guard_charging`: Charging status (charging/not_charging/unknown)
- `sensor.growatt_battery_discharge_guard_sunset_time`: Expected sunset time (timestamp)
- `sensor.growatt_battery_discharge_guard_time_until_sunset`: Time remaining until sunset (duration in seconds)

The sunset entities use your Home Assistant's configured location to calculate accurate sunrise and sunset times, enabling solar-aware battery management and energy planning. The solar panel tilt angle and orientation parameters enhance the accuracy of solar calculations for your specific installation.

### Switches

- `switch.growatt_battery_discharge_guard_enabled`: Enable/disable battery monitoring
- `switch.growatt_battery_discharge_guard_optimization`: Enable/disable battery optimization

## Services

The integration provides the following services:

### `battery_management.set_battery_threshold`

Set a new low battery threshold for discharge protection.

### `battery_management.check_battery_status`

Manually trigger a battery status check from GROWATT servers.

## Development

### Setting Up Development Environment

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e .[dev]
   ```

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black custom_components/

# Lint code  
pylint custom_components/battery_management/

# Type checking
mypy custom_components/battery_management/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- [Issues](https://github.com/your-username/ha-battery-management/issues)
- [Discussions](https://github.com/your-username/ha-battery-management/discussions)
- [Home Assistant Community](https://community.home-assistant.io/)

## Changelog

### v1.0.0
- Initial release
- Battery level monitoring
- Charging status detection
- Configurable thresholds and update intervals
- Battery optimization controls