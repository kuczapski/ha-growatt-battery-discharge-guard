# Solar Power Curve Card

A custom Home Assistant card that displays your solar power forecast as a beautiful curve with real-time indicators.

## Features

- **Live Power Curve**: Shows the complete 24-hour solar power forecast
- **Current Time Indicator**: Blue dashed vertical line showing "Now"
- **Remaining Energy Highlight**: Future production area is colored and labeled
- **Grid Lines**: Easy-to-read time and power grid
- **Responsive Design**: Adapts to your dashboard theme

## Installation

### Method 1: Manual Installation

1. **Download the File**: Save `solar-power-curve-card.js` to your `www` folder:
   ```
   /config/www/solar-power-curve-card.js
   ```

2. **Add Resource**: Go to Settings → Dashboards → Resources and add:
   ```yaml
   url: /local/solar-power-curve-card.js
   type: JavaScript module
   ```

3. **Restart Home Assistant** or refresh your browser

### Method 2: HACS Installation (Future)

This card could be published to HACS for easier installation.

## Configuration

### Basic Configuration

```yaml
type: custom:solar-power-curve-card
entity: sensor.solar_energy_forecast
title: "☀️ Today's Solar Production"
```

### Advanced Configuration

```yaml
type: custom:solar-power-curve-card
entity: sensor.solar_energy_forecast
title: "Solar Power Forecast with Remaining Energy"
```

## Configuration Options

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `entity` | string | **Yes** | - | The solar forecast sensor entity |
| `title` | string | No | "Solar Power Forecast" | Card title |

## Visual Elements

### Color Coding
- **Gray Line**: Past power production (already generated)
- **Orange Line**: Future power forecast
- **Orange Shaded Area**: Remaining energy to be produced
- **Blue Dashed Line**: Current time indicator
- **Orange Text**: Remaining energy amount (e.g., "12.5 kWh remaining")

### Layout
- **X-Axis**: Time (00:00 to 24:00)
- **Y-Axis**: Power output (kW)
- **Grid**: 6-hour time intervals and power level lines
- **Current Time**: Vertical line dividing past from future

## Data Requirements

Your solar forecast entity must provide:
- `full_day_forecast`: Array of forecast points with:
  - `time`: Timestamp
  - `power_kw`: Power output in kilowatts
- `total_energy`: Remaining energy until sunset (kWh)

## Example Dashboard Layout

```yaml
title: Solar Dashboard
views:
  - title: Overview
    cards:
      - type: custom:solar-power-curve-card
        entity: sensor.solar_energy_forecast
        title: "☀️ Today's Solar Production"
      - type: entities
        entities:
          - sensor.battery_level
          - sensor.solar_energy_forecast
```

## Styling

The card automatically adapts to your Home Assistant theme:
- Uses theme colors for text and backgrounds
- Responsive design works on mobile and desktop
- Clean, modern SVG graphics

## Troubleshooting

### Card Not Showing
1. Check that the JavaScript file is in `/config/www/`
2. Verify the resource is added in Dashboard Resources
3. Clear browser cache and refresh

### No Data
1. Ensure your solar forecast entity exists
2. Check that `full_day_forecast` attribute has data
3. Verify entity name matches your configuration

### Entity Not Found
```yaml
# Make sure your entity name is correct
entity: sensor.your_actual_solar_forecast_entity
```

## Customization Ideas

You could extend this card by:
- Adding weather icons based on cloud cover
- Showing battery charge/discharge predictions
- Including historical vs forecast comparison
- Adding click events for detailed views

## Technical Details

- **Framework**: Vanilla JavaScript with Web Components
- **Graphics**: SVG for crisp, scalable visuals
- **Size**: Lightweight (~8KB)
- **Compatibility**: Home Assistant 2021.12+

## Example Output

The card displays:
1. A smooth curve showing power generation throughout the day
2. Past generation in gray (what's already happened)
3. Future generation in orange (what's predicted)
4. Shaded orange area for remaining energy production
5. Blue "Now" line showing current time
6. Text overlay showing remaining kWh (e.g., "8.3 kWh remaining")

Perfect for monitoring your solar production and planning energy usage for the rest of the day! 🌞