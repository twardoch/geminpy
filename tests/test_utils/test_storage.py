# this_file: tests/test_utils/test_storage.py
"""Tests for the SettingsManager."""

from geminpy.utils.storage import SettingsManager


def test_settings_manager_set_get(tmp_path):
    """Verify that SettingsManager can set and get a setting."""
    settings_dir = tmp_path / "settings"
    manager = SettingsManager(settings_dir)

    # Test setting and getting a value
    manager.set("test_key", "test_value")
    assert manager.get("test_key") == "test_value"

    # Test that a non-existent key returns the default
    assert manager.get("non_existent_key") is None
    assert manager.get("non_existent_key", "default") == "default"

    # Test that the settings file was created
    settings_file = settings_dir / "settings.json"
    assert settings_file.exists()
    with open(settings_file) as f:
        content = f.read()
        assert '"test_key": "test_value"' in content
