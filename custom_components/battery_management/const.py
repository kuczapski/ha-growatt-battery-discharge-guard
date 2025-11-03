"""Constants for the Battery Management integration."""

DOMAIN = "battery_management"

# Default values
DEFAULT_NAME = "GROWATT Battery Discharge Guard"
DEFAULT_UPDATE_INTERVAL = 30
DEFAULT_LOW_BATTERY_THRESHOLD = 20
DEFAULT_PV_MAX_POWER = 10.0
DEFAULT_BATTERY_CAPACITY = 10.0
DEFAULT_MIN_DISCHARGE_PERCENTAGE = 10

# Configuration keys
CONF_UPDATE_INTERVAL = "update_interval"
CONF_LOW_BATTERY_THRESHOLD = "low_battery_threshold"
CONF_GROWATT_USERNAME = "growatt_username"
CONF_GROWATT_PASSWORD = "growatt_password"
CONF_PV_MAX_POWER = "pv_max_power"
CONF_BATTERY_CAPACITY = "battery_capacity"
CONF_MIN_DISCHARGE_PERCENTAGE = "min_discharge_percentage"

# Attributes
ATTR_BATTERY_LEVEL = "battery_level"
ATTR_IS_CHARGING = "is_charging"
ATTR_LAST_UPDATED = "last_updated"

# Units of measurement
UNIT_KW = "kW"
UNIT_KWH = "kWh"
UNIT_PERCENTAGE = "%"
UNIT_SECONDS = "s"

# Services
SERVICE_SET_BATTERY_THRESHOLD = "set_battery_threshold"
SERVICE_CHECK_BATTERY_STATUS = "check_battery_status"
