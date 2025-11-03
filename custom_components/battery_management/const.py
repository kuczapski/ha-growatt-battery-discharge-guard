"""Constants for the Battery Management integration."""

DOMAIN = "battery_management"

# Default values
DEFAULT_NAME = "GROWATT Battery Discharge Guard"
DEFAULT_UPDATE_INTERVAL = 30
DEFAULT_LOW_BATTERY_THRESHOLD = 20

# Configuration keys
CONF_UPDATE_INTERVAL = "update_interval"
CONF_LOW_BATTERY_THRESHOLD = "low_battery_threshold"
CONF_GROWATT_USERNAME = "growatt_username"
CONF_GROWATT_PASSWORD = "growatt_password"

# Attributes
ATTR_BATTERY_LEVEL = "battery_level"
ATTR_IS_CHARGING = "is_charging"
ATTR_LAST_UPDATED = "last_updated"

# Services
SERVICE_SET_BATTERY_THRESHOLD = "set_battery_threshold"
SERVICE_CHECK_BATTERY_STATUS = "check_battery_status"
