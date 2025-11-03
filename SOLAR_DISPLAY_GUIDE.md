# Solar Forecast Display Setup Guide

## 🌞 Enhanced Solar Forecast Features

Your solar energy forecast sensor now provides **BOTH** remaining forecast AND full day forecast data:

### **New Attributes Available:**

#### **Remaining Energy (Original)**
- `forecast_5min_intervals`: From NOW until sunset
- `total_energy_kwh`: Remaining energy until sunset
- `peak_power_time_remaining`: Peak power time in remaining forecast
- `peak_power_kw_remaining`: Peak power value remaining
- `average_power_kw_remaining`: Average power remaining

#### **Full Day Forecast (NEW!)**
- `full_day_forecast_5min_intervals`: Complete sunrise to sunset forecast
- `total_daily_energy_kwh`: **Total daily energy production forecast**
- `peak_power_time_daily`: Peak power time for entire day
- `peak_power_kw_daily`: Peak power value for entire day
- `average_power_kw_daily`: Average power for entire day
- `sunrise_time`: When the daily forecast starts
- `sunset_time`: When the daily forecast ends

## 📊 Display Options

### **Option 1: Full Day Curve (Sunrise to Sunset)**
```yaml
type: custom:apexcharts-card
header:
  title: "🌅 Complete Daily Solar Forecast"
  show: true
graph_span: 24h
span:
  start: day
series:
  - entity: sensor.growatt_battery_discharge_guard_solar_energy_forecast
    attribute: full_day_forecast_5min_intervals
    data_generator: |
      return entity.attributes.full_day_forecast_5min_intervals.map((entry) => {
        return [new Date(entry.time).getTime(), entry.power_kw];
      });
    name: "Solar Power (Full Day)"
    color: '#FF9800'
    unit: ' kW'
```

### **Option 2: Remaining vs Full Day Comparison**
```yaml
type: custom:apexcharts-card
header:
  title: "📈 Solar Forecast Comparison"
graph_span: 24h
series:
  # Full day forecast
  - entity: sensor.growatt_battery_discharge_guard_solar_energy_forecast
    attribute: full_day_forecast_5min_intervals
    data_generator: |
      return entity.attributes.full_day_forecast_5min_intervals.map((entry) => {
        return [new Date(entry.time).getTime(), entry.power_kw];
      });
    name: "Full Day Forecast"
    color: '#FFC107'
    opacity: 0.6
    
  # Remaining forecast (highlighted)
  - entity: sensor.growatt_battery_discharge_guard_solar_energy_forecast
    attribute: forecast_5min_intervals
    data_generator: |
      return entity.attributes.forecast_5min_intervals.map((entry) => {
        return [new Date(entry.time).getTime(), entry.power_kw];
      });
    name: "Remaining Forecast"
    color: '#FF5722'
    stroke_width: 3
```

### **Option 3: Daily Summary Cards**
```yaml
type: vertical-stack
cards:
  # Total daily energy card
  - type: entity
    entity: sensor.growatt_battery_discharge_guard_solar_energy_forecast
    attribute: total_daily_energy_kwh
    name: "🌞 Total Daily Solar Energy"
    icon: mdi:solar-power
    
  # Remaining energy card  
  - type: entity
    entity: sensor.growatt_battery_discharge_guard_solar_energy_forecast
    name: "⏰ Remaining Energy Until Sunset"
    icon: mdi:clock-time-four
    
  # Peak power information
  - type: entities
    title: "⚡ Peak Power Information"
    entities:
      - entity: sensor.growatt_battery_discharge_guard_solar_energy_forecast
        attribute: peak_power_kw_daily
        name: "Daily Peak Power"
        icon: mdi:flash
      - entity: sensor.growatt_battery_discharge_guard_solar_energy_forecast
        attribute: peak_power_time_daily
        name: "Peak Time"
        icon: mdi:clock
      - entity: sensor.growatt_battery_discharge_guard_solar_energy_forecast
        attribute: average_power_kw_daily
        name: "Daily Average Power"
        icon: mdi:chart-line
```

### 1. ApexCharts Card (Best for detailed curves)
1. Open HACS in Home Assistant
2. Go to Frontend
3. Search for "ApexCharts Card"
4. Install and restart Home Assistant

### 2. Mini Graph Card (Simple alternative)
1. Open HACS in Home Assistant
2. Go to Frontend  
3. Search for "Mini Graph Card"
4. Install and restart Home Assistant

## Dashboard Configuration Examples

### Comprehensive Solar Dashboard Card
```yaml
type: vertical-stack
cards:
  # Main forecast curve
  - type: custom:apexcharts-card
    header:
      title: "🌞 Solar Power Forecast"
      show: true
    graph_span: 12h
    span:
      start: hour
    apex_config:
      chart:
        type: area
        height: 300
      stroke:
        curve: smooth
        width: 2
      fill:
        type: gradient
        gradient:
          shade: light
          type: vertical
          shadeIntensity: 0.25
          gradientToColors: ['#FFA726']
          inverseColors: false
          opacityFrom: 0.8
          opacityTo: 0.1
      dataLabels:
        enabled: false
      grid:
        show: true
        borderColor: '#e0e0e0'
        strokeDashArray: 2
    series:
      - entity: sensor.growatt_battery_discharge_guard_solar_energy_forecast
        attribute: forecast_5min_intervals
        data_generator: |
          return entity.attributes.forecast_5min_intervals.map((entry) => {
            return [new Date(entry.time).getTime(), entry.power_kw];
          });
        name: "Solar Power"
        color: '#FF9800'
        unit: ' kW'
    yaxis:
      - min: 0
        apex_config:
          title:
            text: "Power (kW)"
            style:
              fontSize: '12px'
    xaxis:
      - apex_config:
          type: datetime
          labels:
            format: 'HH:mm'

  # Summary cards
  - type: horizontal-stack
    cards:
      - type: entity
        entity: sensor.growatt_battery_discharge_guard_solar_energy_forecast
        name: "Total Energy Until Sunset"
        icon: mdi:solar-power
      - type: entity
        entity: sensor.growatt_battery_discharge_guard_solar_energy_forecast
        attribute: peak_power_kw
        name: "Peak Power"
        icon: mdi:flash
      - type: entity
        entity: sensor.growatt_battery_discharge_guard_solar_energy_forecast
        attribute: average_power_kw
        name: "Average Power"
        icon: mdi:chart-line

  # Configuration display
  - type: entities
    title: "⚙️ Solar Panel Configuration"
    entities:
      - entity: sensor.growatt_battery_discharge_guard_solar_energy_forecast
        attribute: panel_tilt_angle
        name: "Panel Tilt"
        icon: mdi:angle-acute
      - entity: sensor.growatt_battery_discharge_guard_solar_energy_forecast
        attribute: panel_orientation
        name: "Panel Orientation"
        icon: mdi:compass
      - entity: sensor.growatt_battery_discharge_guard_solar_energy_forecast
        attribute: pv_max_power_kw
        name: "Max PV Power"
        icon: mdi:lightning-bolt
```

### Simple Mini Graph Version
```yaml
type: custom:mini-graph-card
entities:
  - entity: sensor.growatt_battery_discharge_guard_solar_energy_forecast
    attribute: forecast_5min_intervals
    data_generator: |
      return entity.attributes.forecast_5min_intervals.map((entry) => entry.power_kw);
name: "☀️ Solar Power Forecast"
hours_to_show: 8
points_per_hour: 12
line_width: 3
font_size: 75
animate: true
show:
  graph: line
  fill: fade
  points: hover
  legend: false
  extrema: true
  labels: true
color_thresholds:
  - value: 0
    color: '#424242'
  - value: 1
    color: '#FFC107'
  - value: 3
    color: '#FF9800'
  - value: 6
    color: '#FF5722'
  - value: 9
    color: '#E91E63'
```

## Available Forecast Data Points

Your sensor provides these attributes for visualization:

- `forecast_5min_intervals`: Array of 5-minute predictions
  - `time`: ISO timestamp
  - `power_kw`: Expected power output
  - `solar_elevation`: Sun angle
  - `solar_azimuth`: Sun direction
  - `energy_kwh`: Energy for that interval

- `peak_power_time`: When max power occurs
- `peak_power_kw`: Maximum power value
- `average_power_kw`: Average power for the day
- `sunset_time`: When forecast ends
- `total_energy_kwh`: Total expected energy

## Tips for Best Display

1. **Update Frequency**: The forecast updates automatically with HA
2. **Performance**: For performance, limit graph to 6-12 hours
3. **Mobile**: Use smaller cards for mobile dashboards
4. **Colors**: Use solar-themed colors (oranges, yellows)
5. **Combine**: Show alongside battery level and consumption data