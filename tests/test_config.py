# -*- coding: utf-8 -*-

import os
from unittest.mock import call, patch

import pytest

from slow_start_rewatch.config import Config
from slow_start_rewatch.config_storage import ConfigStorage
from tests.conftest import REFRESH_TOKEN, TEST_ROOT_DIR

EXAMPLE_CONFIG_FILE = os.path.join(
    TEST_ROOT_DIR,
    "test_config",
    "config_example.yml",
)


def test_default_config():
    """Test that default config is loaded and contains mandatory items."""
    config = Config()

    assert "data_dir" in config
    assert "refresh_token_file" in config
    assert "Slow Start" in config["reddit.user_agent"]


def test_custom_config():
    """Test that default config is loaded and populated."""
    config = Config(EXAMPLE_CONFIG_FILE)

    assert config["heartwarming_anime.name"] == "Slow Start"
    assert "cute_girls" in config
    assert "pesky_boys" not in config
    assert os.path.expanduser("~") in config["data_dir"]
    assert "{0}slow_start".format(os.path.sep) in config["refresh_token_file"]


def test_config_interface():
    """Test setting config keys."""
    config = Config(EXAMPLE_CONFIG_FILE)

    with pytest.raises(KeyError):
        config["slow_start"]["second_season"] = None

    config["slow_start"] = {}
    config["slow_start.second_season"] = "When?"
    assert config["slow_start"]["second_season"] == "When?"


@patch.object(ConfigStorage, "load_refresh_token")
def test_refresh_token_getter(mock_load):
    """
    Test getting the token.

    When the token is ``None`` it's loaded from the storage.

    When the token is set already a cached value is used instead of loading.
    """
    config = Config()
    mock_load.side_effect = [
        None,
        REFRESH_TOKEN,
        "oishiku_nare",
    ]

    assert config.refresh_token is None
    assert config.refresh_token == REFRESH_TOKEN
    assert config.refresh_token == REFRESH_TOKEN
    assert mock_load.call_count == 2


@patch.object(ConfigStorage, "load_refresh_token")
@patch.object(ConfigStorage, "delete_refresh_token")
@patch.object(ConfigStorage, "save_refresh_token")
def test_refresh_token_setter(mock_save, mock_delete, mock_load):
    """
    Test setting the token.

    The token should be saved when the property is set to a string and deleted
    when it's set to ``None``.

    Loading must be mocked to allow assertion of the empty value.
    """
    config = Config()

    config.refresh_token = REFRESH_TOKEN
    assert mock_save.call_args == call(REFRESH_TOKEN)
    assert config.refresh_token == REFRESH_TOKEN

    config.refresh_token = None
    mock_load.return_value = None
    assert mock_delete.call_count == 1
    assert config.refresh_token is None
    assert mock_load.call_count == 1
