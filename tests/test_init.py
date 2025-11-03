"""Tests for the Battery Management integration."""

import pytest
from unittest.mock import MagicMock, AsyncMock


@pytest.fixture
def mock_config_entry():
    """Return a mock config entry."""
    return {
        "name": "Test GROWATT Battery Discharge Guard",
        "growatt_username": "test_user",
        "growatt_password": "test_password",
        "pv_max_power": 15.0,
        "battery_capacity": 12.5,
        "min_discharge_percentage": 15,
        "update_interval": 30,
        "low_battery_threshold": 20,
    }


@pytest.fixture
def mock_hass():
    """Return a mock Home Assistant instance."""
    hass = MagicMock()
    hass.data = {}
    # Make config_entries methods async
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    return hass


@pytest.mark.asyncio
async def test_setup_integration(mock_hass, mock_config_entry):
    """Test the integration setup."""
    # Import after mocks are in place
    from custom_components.battery_management import async_setup_entry
    from custom_components.battery_management.const import DOMAIN

    # Create a mock config entry
    config_entry = MagicMock()
    config_entry.data = mock_config_entry
    config_entry.entry_id = "test_entry"

    # Test setup
    result = await async_setup_entry(mock_hass, config_entry)

    assert result is True
    assert DOMAIN in mock_hass.data
    # Verify the async_forward_entry_setups was called
    mock_hass.config_entries.async_forward_entry_setups.assert_called_once()


def test_constants():
    """Test that constants are properly defined."""
    from custom_components.battery_management.const import (
        DOMAIN,
        DEFAULT_NAME,
        DEFAULT_UPDATE_INTERVAL,
        DEFAULT_LOW_BATTERY_THRESHOLD,
    )

    assert DOMAIN == "battery_management"
    assert DEFAULT_NAME == "GROWATT Battery Discharge Guard"
    assert DEFAULT_UPDATE_INTERVAL == 30
    assert DEFAULT_LOW_BATTERY_THRESHOLD == 20


def test_manifest_exists():
    """Test that manifest.json exists and has required fields."""
    import json
    import os

    manifest_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "custom_components",
        "battery_management",
        "manifest.json",
    )

    assert os.path.exists(manifest_path), "manifest.json should exist"

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    required_fields = ["domain", "name", "version", "homeassistant"]
    for field in required_fields:
        assert field in manifest, f"manifest.json should contain {field}"
