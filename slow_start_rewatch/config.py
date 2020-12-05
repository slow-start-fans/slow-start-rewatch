# -*- coding: utf-8 -*-

import os
from string import Template
from typing import Optional

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

    def __init__(self, filename: str = DEFAULT_CONFIG_FILENAME) -> None:
        """Initialize Config."""
        log.debug("config_load", filename=filename)

        config_list = [os.path.join(ROOT_DIR, filename)]

        self.config = Cut(anyconfig.load(config_list))

        self._substitute_placeholders()

        self.storage = ConfigStorage(self.config["refresh_token_file"])

        self._refresh_token: Optional[str] = None

    def __getitem__(self, key):
        """Return the config item."""
        return self.config[key]

    def __setitem__(self, key, item_value):
        """Set the config item."""
        self.config[key] = item_value

    def __contains__(self, key):
        """Return true if an item exists in the config."""
        return key in self.config

    @property
    def refresh_token(self) -> Optional[str]:
        """
        Get the refresh token.

        Try to load the token if not set.
        """
        if not self._refresh_token:
            self._refresh_token = self.storage.load_refresh_token()

        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, refresh_token: Optional[str]) -> None:
        """
        Set and save the refresh token.

        If the value is set to None delete the stored token.
        """
        if refresh_token:
            self._refresh_token = refresh_token.strip()
            self.storage.save_refresh_token(self._refresh_token)
        else:
            self._refresh_token = None
            self.storage.delete_refresh_token()

    def _substitute_placeholders(self) -> None:
        """Substitute the placeholders in the config."""
        mapping = {
            "home_dir": HOME_DIR,
            "ps": os.path.sep,
            "version": version(),
        }
        keys = [
            "data_dir",
            "scheduled_post_file",
            "refresh_token_file",
            "reddit.user_agent",
        ]

        log.debug("config_substitute", mapping=mapping, keys=keys)

        for key in keys:
            self.config[key] = Template(self.config[key]).safe_substitute(
                mapping,
            )
