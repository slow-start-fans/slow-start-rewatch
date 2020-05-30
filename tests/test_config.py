# -*- coding: utf-8 -*-

import os

import pytest

from slow_start_rewatch.config import Config

TEST_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
EXAMPLE_CONFIG_FILE = os.path.join(
    TEST_ROOT_DIR,
    "test_config",
    "config_example.yml",
)


def test_default_config():
    """Test that default config is loaded."""
    config = Config()

    assert "data_dir" in config
    assert "Slow Start" in config["reddit.user_agent"]


def test_custom_config():
    """Test that default config is loaded and populated."""
    config = Config(EXAMPLE_CONFIG_FILE)

    assert config["heartwarming_anime.name"] == "Slow Start"
    assert "cute_girls" in config
    assert "pesky_boys" not in config
    assert os.path.expanduser("~") in config["data_dir"]
    assert "{0}slow_start".format(os.path.sep) in config["data_dir"]


def test_config_interface():
    """Test setting config keys."""
    config = Config(EXAMPLE_CONFIG_FILE)

    with pytest.raises(KeyError):
        config["slow_start"]["second_season"] = None

    config["slow_start.second_season"] = "When?"
    assert config["slow_start"]["second_season"] == "When?"
