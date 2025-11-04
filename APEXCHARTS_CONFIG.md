# ApexCharts Card Configuration for Solar Energy Forecast

This configuration displays the daily solar energy forecast from your GROWATT Battery Discharge Guard integration.

## Basic Forecast Chart

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: "☀️ Daily Solar Energy Forecast"
  show_states: true
  colorize_states: true
graph_span: 24h
span:
  start: day
now:
  show: true
  label: Now
yaxis:
  - id: power
    opposite: true
    decimals: 1
    apex_config:
      title:
        text: "Power (kW)"
  - id: energy
    decimals: 2
    apex_config:
      title:
        text: "Energy (kWh)"
series:
  - entity: sensor.solar_energy_forecast
    name: "Energy Production"
    yaxis_id: energy
    type: column
    color: orange
    data_generator: |
      return entity.attributes.full_day_forecast.map((entry) => {
        return [new Date(entry.time).getTime(), entry.energy_15min_kwh];
      });
  - entity: sensor.solar_energy_forecast
    name: "Power Output"
    yaxis_id: power
    type: line
    color: red
    stroke_width: 2
    data_generator: |
      return entity.attributes.full_day_forecast.map((entry) => {
        return [new Date(entry.time).getTime(), entry.power_kw];
      });
```

## Advanced Forecast Chart with Irradiance

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: "☀️ Solar Forecast - Power, Energy & Irradiance"
  show_states: true
  colorize_states: true
graph_span: 24h
span:
  start: day
now:
  show: true
  label: Now
  color: purple
yaxis:
  - id: power
    opposite: false
    decimals: 1
    min: 0
    apex_config:
      title:
        text: "Power (kW)"
  - id: energy
    opposite: true
    decimals: 2
    min: 0
    apex_config:
      title:
        text: "Energy (kWh)"
  - id: irradiance
    opposite: true
    decimals: 0
    min: 0
    apex_config:
      title:
        text: "Irradiance (W/m²)"
series:
  - entity: sensor.solar_energy_forecast
    name: "15-min Energy"
    yaxis_id: energy
    type: column
    color: "#FFA726"
    opacity: 0.7
    data_generator: |
      return entity.attributes.full_day_forecast.map((entry) => {
        return [new Date(entry.time).getTime(), entry.energy_15min_kwh];
      });
  - entity: sensor.solar_energy_forecast
    name: "Power Output"
    yaxis_id: power
    type: line
    color: "#FF5722"
    stroke_width: 3
    data_generator: |
      return entity.attributes.full_day_forecast.map((entry) => {
        return [new Date(entry.time).getTime(), entry.power_kw];
      });
  - entity: sensor.solar_energy_forecast
    name: "Solar Irradiance"
    yaxis_id: irradiance
    type: area
    color: "#FFEB3B"
    opacity: 0.3
    stroke_width: 1
    data_generator: |
      return entity.attributes.full_day_forecast.map((entry) => {
        return [new Date(entry.time).getTime(), entry.irradiance];
      });
```

## Compact Daily Summary Card

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: "⚡ Today's Solar Production"
  show_states: true
  colorize_states: true
graph_span: 24h
span:
  start: day
now:
  show: true
  label: Now
apex_config:
  chart:
    height: 250px
  legend:
    show: false
  tooltip:
    x:
      format: "HH:mm"
yaxis:
  - id: power
    decimals: 1
    min: 0
    apex_config:
      title:
        text: "Power (kW)"
series:
  - entity: sensor.solar_energy_forecast
    name: "Solar Power"
    yaxis_id: power
    type: area
    color: "#FF9800"
    stroke_width: 2
    fill_raw: last
    data_generator: |
      return entity.attributes.full_day_forecast.map((entry) => {
        return [new Date(entry.time).getTime(), entry.power_kw];
      });
```

## Remaining vs Total Energy Card

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: "🔋 Remaining Solar Energy Until Sunset"
  show_states: true
  colorize_states: true
graph_span: 12h
span:
  start: hour
  offset: -1h
now:
  show: true
  label: Now
yaxis:
  - id: energy
    decimals: 2
    min: 0
    apex_config:
      title:
        text: "Energy (kWh)"
series:
  - entity: sensor.solar_energy_forecast
    name: "Remaining Energy"
    yaxis_id: energy
    type: column
    color: "#4CAF50"
    data_generator: |
      return entity.attributes.forecast.map((entry) => {
        return [new Date(entry.time).getTime(), entry.energy_15min_kwh];
      });
```

## Installation Notes

1. **Install ApexCharts Card** via HACS:
   - Go to HACS → Frontend
   - Search for "ApexCharts Card"
   - Install and add to resources

2. **Entity Name**: Replace `sensor.solar_energy_forecast` with your actual sensor entity name from the GROWATT integration

3. **Customize Colors**: Adjust the color schemes to match your dashboard theme

4. **Time Zones**: The charts will automatically use your Home Assistant timezone

## Available Data Points

Your solar forecast sensor provides these attributes for charting:
- `full_day_forecast`: Complete 24-hour forecast (96 intervals of 15 minutes each)
- `forecast`: Remaining forecast until sunset
- `total_daily_energy`: Total expected energy for the day
- `total_energy`: Remaining energy until sunset

Each forecast entry contains:
- `time`: Timestamp
- `power_kw`: Power output in kW
- `energy_15min_kwh`: Energy for 15-minute interval
- `irradiance`: Solar irradiance in W/m²
- `solar_elevation`: Sun elevation angle
- `solar_azimuth`: Sun azimuth angle

## Tips

- Use the **Basic Forecast Chart** for a clean overview
- Use the **Advanced Chart** to see correlation between irradiance and power
- Use the **Compact Card** for dashboard space efficiency
- Use the **Remaining Energy Card** to track what's left for the day

Choose the configuration that best fits your dashboard layout and information needs!

## Custom Solar Power Curve Card

For a more interactive and visually appealing display, check out our **Custom Solar Power Curve Card** (`solar-power-curve-card.js`). This custom card provides:

- **Real-time current time indicator** with a vertical line
- **Color-coded past vs future** power generation
- **Highlighted remaining energy area** with kWh overlay
- **Clean SVG graphics** that adapt to your theme
- **Lightweight and fast** rendering

See `SOLAR_POWER_CURVE_CARD.md` for installation and configuration details.

**Quick setup:**
```yaml
type: custom:solar-power-curve-card
entity: sensor.solar_energy_forecast
title: "☀️ Today's Solar Production"
```