"""Test configuration for pytest."""

import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Create proper mock modules for homeassistant
def create_mock_module(name):
    """Create a mock module with common attributes."""
    mock = MagicMock()
    mock.__name__ = name
    return mock


# Mock homeassistant modules with Platform enum
ha_const_mock = create_mock_module("homeassistant.const")
ha_const_mock.Platform = MagicMock()
ha_const_mock.Platform.SENSOR = "sensor"
ha_const_mock.Platform.SWITCH = "switch"
ha_const_mock.PERCENTAGE = "%"

ha_core_mock = create_mock_module("homeassistant.core")
ha_core_mock.HomeAssistant = MagicMock()
ha_core_mock.callback = lambda func: func

ha_setup_mock = create_mock_module("homeassistant.setup")
ha_setup_mock.async_setup_component = MagicMock(return_value=True)

ha_config_entries_mock = create_mock_module("homeassistant.config_entries")
ha_config_entries_mock.ConfigEntry = MagicMock()

sys.modules["homeassistant"] = create_mock_module("homeassistant")
sys.modules["homeassistant.core"] = ha_core_mock
sys.modules["homeassistant.const"] = ha_const_mock
sys.modules["homeassistant.setup"] = ha_setup_mock
sys.modules["homeassistant.config_entries"] = ha_config_entries_mock
sys.modules["homeassistant.helpers"] = create_mock_module("homeassistant.helpers")
sys.modules["homeassistant.components"] = create_mock_module("homeassistant.components")
sys.modules["homeassistant.components.sensor"] = create_mock_module(
    "homeassistant.components.sensor"
)
sys.modules["homeassistant.components.switch"] = create_mock_module(
    "homeassistant.components.switch"
)
sys.modules["homeassistant.helpers.entity_platform"] = create_mock_module(
    "homeassistant.helpers.entity_platform"
)
sys.modules["homeassistant.helpers.update_coordinator"] = create_mock_module(
    "homeassistant.helpers.update_coordinator"
)
sys.modules["homeassistant.data_entry_flow"] = create_mock_module(
    "homeassistant.data_entry_flow"
)
sys.modules["homeassistant.helpers.config_validation"] = create_mock_module(
    "homeassistant.helpers.config_validation"
)
sys.modules["voluptuous"] = create_mock_module("voluptuous")


@pytest.fixture
def hass():
    """Return a mock Home Assistant instance."""

    class MockHass:
        def __init__(self):
            self.data = {}

        async def async_setup_component(self, domain, config):
            return True

    return MockHass()
