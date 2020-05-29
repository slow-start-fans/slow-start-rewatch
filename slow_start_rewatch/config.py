# -*- coding: utf-8 -*-

import os

import anyconfig
from dotty_dict import dotty
from structlog import get_logger

DEFAULT_CONFIG_FILENAME = "config_default.yml"
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
HOME_DIR = os.path.expanduser("~")

log = get_logger()


class Config(object):
    """Provides configuration for the Slow Start Rewatch."""

    def __init__(self, filename: str = DEFAULT_CONFIG_FILENAME) -> None:
        """Initialize Config."""
        log.debug("config_load", filename=filename)

        config_list = [os.path.join(ROOT_DIR, filename)]

        self.config = dotty(anyconfig.load(config_list))

    def __getitem__(self, key):
        """Return the config item."""
        return self.config[key]

    def __setitem__(self, key, item_value):
        """Set the config item."""
        self.config[key] = item_value

    def __contains__(self, key):
        """Return true if an item exists in the config."""
        return key in self.config