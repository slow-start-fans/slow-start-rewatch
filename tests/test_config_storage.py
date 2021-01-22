# -*- coding: utf-8 -*-

import os

import pytest

from slow_start_rewatch.config_storage import ConfigStorage
from slow_start_rewatch.exceptions import ConfigError, InvalidLocalConfig


def test_saving_to_existing_directory(tmpdir, config_data):
    """Test that the config is saved to an existing directory."""
    existing_path = tmpdir.join("config_local.yml")
    config_storage = ConfigStorage(existing_path)

    assert not os.path.exists(existing_path)

    config_storage.save(config_data)

    with open(existing_path) as config_file:
        assert "refresh_token: moe_moe_kyun" in config_file.read()


def test_saving_to_new_directory(tmpdir, config_data):
    """Test that a new directory is created before saving the config."""
    new_directory = tmpdir.join("new_directory")
    assert not os.path.exists(new_directory)

    new_path = new_directory.join("config_local.yml")
    config_storage = ConfigStorage(new_path)

    config_storage.save(config_data)

    assert os.path.exists(new_directory)

    with open(new_path) as config_file:
        assert "refresh_token: moe_moe_kyun" in config_file.read()


def test_saving_incomplete_config(tmpdir):
    """Test error handling of saving config with missing items."""
    existing_path = tmpdir.join("config_local.yml")
    config_storage = ConfigStorage(existing_path)

    config_data = {"refresh_token": "moe_moe_kyun"}

    with pytest.raises(ConfigError):
        config_storage.save(config_data)


def test_loading_existing_file(tmpdir):
    """Test that the config is loaded from the existing file."""
    config_path = tmpdir.join("config_local.yml")

    with open(config_path, "w") as config_file:
        config_file.write("refresh_token: moe_moe_kyun")

    config_storage = ConfigStorage(config_path)

    # Override the default list of stored items
    config_storage.locally_stored_items = ["refresh_token"]

    assert config_storage.load() == {"refresh_token": "moe_moe_kyun"}


def test_loading_nonexistent_file(tmpdir):
    """Test that loading a nonexistent file creates empty config items."""
    config_path = tmpdir.join("config_local.yml")
    assert not os.path.exists(config_path)

    config_storage = ConfigStorage(config_path)

    config_data = config_storage.load()

    assert "refresh_token" in config_data
    assert len(config_data) == len(config_storage.locally_stored_items)


def test_loading_corrupted_file(tmpdir):
    """Test error handling of loading a corrupted file."""
    config_path = tmpdir.join("config_local.yml")

    corrupted_yaml = """refresh_token: |
Removed indentation to cause YAML parsing error.
"""

    with open(config_path, "w") as config_file:
        config_file.write(corrupted_yaml)

    config_storage = ConfigStorage(config_path)

    with pytest.raises(InvalidLocalConfig):
        config_storage.load()


def test_loading_incomplete_file(tmpdir):
    """Test error handling of loading an incomplete config file."""
    config_path = tmpdir.join("config_local.yml")

    config_yaml = "refresh_token: moe_moe_kyun"

    with open(config_path, "w") as config_file:
        config_file.write(config_yaml)

    config_storage = ConfigStorage(config_path)

    with pytest.raises(InvalidLocalConfig):
        config_storage.load()


@pytest.fixture()
def config_data():
    """Return mock Config data."""
    return {
        "refresh_token": "moe_moe_kyun",
        "schedule_file": "slow_start_rewatch/schedule.yml",
    }
