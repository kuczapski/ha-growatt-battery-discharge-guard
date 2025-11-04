class SolarPowerCurveCard extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this._boundThemeChangeHandler = this.handleThemeChange.bind(this);
    }

    setConfig(config) {
        if (!config.entity) {
            throw new Error('You need to define an entity');
        }
        this.config = config;
    }

    connectedCallback() {
        // Listen for theme changes
        this.observeThemeChanges();
    }

    disconnectedCallback() {
        // Clean up observers
        if (this._themeObserver) {
            this._themeObserver.disconnect();
        }
    }

    observeThemeChanges() {
        // Watch for changes to data-theme attribute on body or html
        const targets = [document.body, document.documentElement];

        this._themeObserver = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' &&
                    (mutation.attributeName === 'data-theme' || mutation.attributeName === 'class')) {
                    this.handleThemeChange();
                }
            });
        });

        targets.forEach(target => {
            this._themeObserver.observe(target, {
                attributes: true,
                attributeFilter: ['data-theme', 'class']
            });
        });
    }

    handleThemeChange() {
        // Re-render the card when theme changes
        if (this._hass) {
            this.updateCard();
        }
    }

    set hass(hass) {
        this._hass = hass;
        this.updateCard();
    }

    updateCard() {
        const entity = this._hass.states[this.config.entity];
        if (!entity) {
            this.shadowRoot.innerHTML = `
        <ha-card>
          <div class="error">Entity "${this.config.entity}" not found</div>
        </ha-card>
      `;
            return;
        }

        const forecast = entity.attributes.full_day_forecast || [];
        const remainingEnergy = entity.attributes.total_energy || 0;

        if (forecast.length === 0) {
            this.shadowRoot.innerHTML = `
        <ha-card>
          <div class="no-data">No forecast data available</div>
        </ha-card>
      `;
            return;
        }

        this.render(forecast, remainingEnergy);
    }

    render(forecast, remainingEnergy) {
        const now = new Date();
        const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const endOfDay = new Date(startOfDay.getTime() + 24 * 60 * 60 * 1000);

        // Chart dimensions - more compact
        const width = 380;
        const height = 120;
        const margin = { top: 15, right: 15, bottom: 15, left: 15 };
        const chartWidth = width - margin.left - margin.right;
        const chartHeight = height - margin.top - margin.bottom;

        // Find max power for scaling
        const maxPower = Math.max(...forecast.map(f => f.power_kw));
        const powerScale = chartHeight / maxPower;

        // Time scale (24 hours)
        const timeScale = chartWidth / (24 * 60 * 60 * 1000);

        // Generate SVG path for power curve
        let pathData = '';
        let futurePathData = '';
        const currentTimeMs = now.getTime();

        forecast.forEach((point, index) => {
            const pointTime = new Date(point.time).getTime();
            const x = margin.left + (pointTime - startOfDay.getTime()) * timeScale;
            const y = margin.top + chartHeight - (point.power_kw * powerScale);

            const command = index === 0 ? 'M' : 'L';
            const pointStr = `${command} ${x} ${y}`;

            if (pointTime <= currentTimeMs) {
                pathData += pointStr + ' ';
            } else {
                if (futurePathData === '') {
                    // Start future path from current position
                    const lastPastPoint = forecast[Math.max(0, index - 1)];
                    if (lastPastPoint) {
                        const lastX = margin.left + (new Date(lastPastPoint.time).getTime() - startOfDay.getTime()) * timeScale;
                        const lastY = margin.top + chartHeight - (lastPastPoint.power_kw * powerScale);
                        futurePathData = `M ${lastX} ${lastY} `;
                    }
                }
                futurePathData += pointStr + ' ';
            }
        });

        // Create area fill for future energy
        let futureAreaPath = '';
        if (futurePathData) {
            const futurePoints = forecast.filter(f => new Date(f.time).getTime() > currentTimeMs);
            if (futurePoints.length > 0) {
                const firstFutureTime = new Date(futurePoints[0].time).getTime();
                const lastFutureTime = new Date(futurePoints[futurePoints.length - 1].time).getTime();
                const startX = margin.left + (firstFutureTime - startOfDay.getTime()) * timeScale;
                const endX = margin.left + (lastFutureTime - startOfDay.getTime()) * timeScale;

                futureAreaPath = futurePathData +
                    `L ${endX} ${margin.top + chartHeight} ` +
                    `L ${startX} ${margin.top + chartHeight} Z`;
            }
        }

        // Current time line position
        const currentTimeX = margin.left + (currentTimeMs - startOfDay.getTime()) * timeScale;

        // Format remaining energy text - just value and unit
        const energyText = `${remainingEnergy.toFixed(1)} kWh`;

        // Calculate text position (top right area)
        const textX = width - 25;
        const textY = margin.top + 12;

        const cardTitle = this.config.title || 'Solar Power Forecast';

        // Simplified theme detection - check multiple sources
        const isDarkMode = document.body.hasAttribute('data-theme') ||
            document.documentElement.hasAttribute('data-theme') ||
            document.body.classList.contains('dark') ||
            window.matchMedia?.('(prefers-color-scheme: dark)').matches;

        // Define theme-specific colors
        const themeColors = isDarkMode ? {
            cardBackground: '#1c1c1c',
            primaryText: '#e1e1e1',
            secondaryText: '#9e9e9e',
            dividerColor: '#404040',
            cardShadow: '0 2px 8px rgba(0, 0, 0, 0.3)'
        } : {
            cardBackground: 'white',
            primaryText: '#212121',
            secondaryText: '#727272',
            dividerColor: '#e0e0e0',
            cardShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
        };

        this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          width: 100%;
        }
        ha-card {
          display: block;
          padding: 16px;
          background: ${themeColors.cardBackground};
          border-radius: 12px;
          box-shadow: ${themeColors.cardShadow};
          margin: 0;
          width: 100%;
          min-height: 160px;
          box-sizing: border-box;
        }
        .card-title {
          font-size: 1.1em;
          font-weight: 500;
          margin: 0 0 12px 0;
          color: ${themeColors.primaryText};
          display: block;
        }
        .chart-container {
          width: 100%;
          height: auto;
          display: block;
          margin: 0;
          padding: 0;
        }
        .chart-svg {
          display: block;
          width: 100%;
          height: auto;
          max-width: none;
        }
        .power-curve {
          stroke: #ff6b35;
          stroke-width: 2;
          fill: none;
        }
        .power-curve-past {
          stroke: ${isDarkMode ? '#888' : '#666'};
          stroke-width: 2;
          fill: none;
        }
        .future-area {
          fill: rgba(255, 107, 53, 0.2);
          stroke: none;
        }
        .current-time-line {
          stroke: #2196f3;
          stroke-width: 2;
          stroke-dasharray: 5,5;
        }
        .grid-line {
          stroke: ${themeColors.dividerColor};
          stroke-width: 0.5;
          opacity: 0.3;
        }
        .energy-text {
          font-size: 12px;
          font-weight: 600;
          fill: #ff6b35;
          text-anchor: end;
        }
        .error, .no-data {
          padding: 20px;
          text-align: center;
          color: #ff5252;
          background: ${themeColors.cardBackground};
        }
      </style>
      <ha-card>
        <div class="card-title">${cardTitle}</div>
        <div class="chart-container">
          <svg class="chart-svg" viewBox="0 0 ${width} ${height}" preserveAspectRatio="xMidYMid meet">
            <!-- Minimal grid lines -->
            ${this.generateMinimalGridLines(width, height, margin)}
            
            <!-- Future area fill -->
            ${futureAreaPath ? `<path d="${futureAreaPath}" class="future-area"/>` : ''}
            
            <!-- Power curves -->
            ${pathData ? `<path d="${pathData}" class="power-curve-past"/>` : ''}
            ${futurePathData ? `<path d="${futurePathData}" class="power-curve"/>` : ''}
            
            <!-- Current time line -->
            <line x1="${currentTimeX}" y1="${margin.top}" 
                  x2="${currentTimeX}" y2="${margin.top + chartHeight}" 
                  class="current-time-line"/>
            
            <!-- Energy remaining text (only numerical value and unit) -->
            ${remainingEnergy > 0 ? `<text x="${textX}" y="${textY}" class="energy-text">${energyText}</text>` : ''}
          </svg>
        </div>
      </ha-card>
    `;
    }

    generateMinimalGridLines(width, height, margin) {
        const lines = [];
        // Just a subtle bottom border
        const bottomY = height - margin.bottom;
        lines.push(`<line x1="${margin.left}" y1="${bottomY}" x2="${width - margin.right}" y2="${bottomY}" class="grid-line"/>`);
        return lines.join('');
    }

    getCardSize() {
        return 3;
    }
}

customElements.define('solar-power-curve-card', SolarPowerCurveCard);

// Register the card
window.customCards = window.customCards || [];
window.customCards.push({
    type: 'solar-power-curve-card',
    name: 'Solar Power Curve Card',
    description: 'A custom card that displays solar power forecast with current time indicator'
});