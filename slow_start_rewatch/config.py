# -*- coding: utf-8 -*-

import os
from string import Template

import anyconfig
from scalpl import Cut
from structlog import get_logger

from slow_start_rewatch.config_storage import ConfigStorage
from slow_start_rewatch.version import version

DEFAULT_CONFIG_FILENAME = "config_default.yml"
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
HOME_DIR = os.path.expanduser("~")

log = get_logger()


class Config(object):
    """Provides configuration for the Slow Start Rewatch."""

    def __init__(
        self,
        filename: str = DEFAULT_CONFIG_FILENAME,
    ) -> None:
        """Initialize Config."""
        log.debug("default_config_load", filename=filename)

        config_list = [os.path.join(ROOT_DIR, filename)]

        self.config = Cut(anyconfig.load(config_list))

        self._substitute_placeholders()

        self.storage = ConfigStorage(self.config["local_config_file"])

    def __getitem__(self, key):
        """Return the config item."""
        return self.config[key]

    def __setitem__(self, key, item_value) -> None:
        """Set the config item."""
        if key in self.config and self.config[key] == item_value:
            return

        log.debug("config_save", key=key, item_value=item_value)
        self.config[key] = item_value
        self.storage.save(self.config)

    def __contains__(self, key):
        """Return true if an item exists in the config."""
        return key in self.config

    def load(self) -> None:
        """Load config items from the local storage."""
        self.config.update(self.storage.load())

    def _substitute_placeholders(self) -> None:
        """Substitute the placeholders in the config."""
        mapping = {
            "home_dir": HOME_DIR,
            "ps": os.path.sep,
            "version": version(),
        }
        keys = [
            "data_dir",
            "schedule_file",
            "local_config_file",
            "reddit.user_agent",
        ]

        log.debug("config_substitute", mapping=mapping, keys=keys)

        for key in keys:
            self.config[key] = Template(self.config[key]).safe_substitute(
                mapping,
            )
