# -*- coding: utf-8 -*-

import os
from unittest.mock import patch

import pytest

from slow_start_rewatch.config import Config
from slow_start_rewatch.config_storage import ConfigStorage
from tests.conftest import TEST_ROOT_DIR

EXAMPLE_CONFIG_FILE = os.path.join(
    TEST_ROOT_DIR,
    "test_config",
    "config_example.yml",
)


@patch.object(ConfigStorage, "load")
def test_default_config(mock_load):
    """Test that default config is loaded and contains mandatory items."""
    config = Config()
    config.load()

    assert "data_dir" in config
    assert "local_config_file" in config
    assert "Slow Start" in config["reddit.user_agent"]
    assert mock_load.call_count == 1


def test_custom_config():
    """Test that default config is loaded and populated."""
    config = Config(EXAMPLE_CONFIG_FILE)

    assert config["heartwarming_anime.name"] == "Slow Start"
    assert "cute_girls" in config
    assert "pesky_boys" not in config
    assert os.path.expanduser("~") in config["data_dir"]
    assert "{0}slow_start".format(os.path.sep) in config["local_config_file"]


@patch.object(ConfigStorage, "save")
def test_config_interface(mock_save):
    """
    Test setting config keys.

    Check that the config is not saved when the value of the item is unchanged.
    """
    config = Config(EXAMPLE_CONFIG_FILE)

    with pytest.raises(KeyError):
        config["slow_start"]["second_season"] = None

    config["slow_start"] = {}
    config["slow_start.second_season"] = "When?"
    assert config["slow_start"]["second_season"] == "When?"
    assert mock_save.call_count == 2

    config["slow_start.second_season"] = "When?"
    assert mock_save.call_count == 2
