# -*- coding: utf-8 -*-

import os
from pathlib import Path
from typing import Dict, Optional

from ruamel.yaml import YAML, YAMLError  # type: ignore
from scalpl import Cut
from structlog import get_logger

from slow_start_rewatch.exceptions import (
    ConfigError,
    InvalidLocalConfig,
    MissingLocalConfig,
)

log = get_logger()


class ConfigStorage(object):
    """Provides methods for storage of config data."""

    def __init__(self, local_config_file: str) -> None:
        """Initialize ConfigStorage."""
        self.local_config_file = local_config_file

        self.locally_stored_items = [
            "refresh_token",
            "schedule_wiki_url",
            "schedule_file",
        ]

    def load(self) -> Dict[str, Optional[str]]:
        """
        Load the local config.

        Create empty config items if the local file does no exist.
        """
        try:
            config_data = self.parse_stored_data(self.load_from_file())
        except MissingLocalConfig:
            log.info("local_config_create_empty")
            config_data = {
                key: None
                for key in self.locally_stored_items
            }

        return config_data

    def load_from_file(self) -> Dict[str, Optional[str]]:
        """Load stored config data from a file if exists."""
        log.debug("local_config_file_read", path=self.local_config_file)
        try:
            with open(self.local_config_file) as config_file:
                yaml_content = config_file.read()
        except IOError:
            log.debug("local_config_file_missing", path=self.local_config_file)
            raise MissingLocalConfig

        yaml = YAML(typ="safe")

        try:
            stored_data = yaml.load(yaml_content)
        except (YAMLError, AttributeError) as yaml_error:
            log.exception("local_config_file_invalid")
            raise InvalidLocalConfig(
                "Failed to parse the local config.",
            ) from yaml_error

        return stored_data

    def parse_stored_data(
        self,
        stored_data: Dict[str, Optional[str]],
    ) -> Dict[str, Optional[str]]:
        """Parse predefined items from the loaded config data."""
        try:
            config_data = {
                key: stored_data[key]
                for key
                in self.locally_stored_items
            }
        except KeyError as error:
            log.exception("local_config_key_missing")
            raise InvalidLocalConfig(
                "Missing items in the local config data.",
            ) from error

        return config_data

    def save(self, config_data: Cut) -> None:
        """
        Save config data to a file.

        Create the directory if not exist.
        """
        log.info("local_config_save", path=self.local_config_file)

        Path(os.path.dirname(self.local_config_file)).mkdir(
            parents=True,
            exist_ok=True,
        )

        yaml = YAML(typ="safe")
        yaml.default_flow_style = False
        yaml_data = self.store_config_data(config_data)

        with open(self.local_config_file, "w") as config_file:
            yaml.dump(yaml_data, config_file)

    def store_config_data(
        self,
        config_data: Dict[str, Optional[str]],
    ) -> Dict[str, Optional[str]]:
        """Store predefined congig items."""
        try:
            yaml_data = {
                key: config_data[key]
                for key
                in self.locally_stored_items
            }
        except KeyError as error:
            log.exception("config_key_missing")
            raise ConfigError(
                "Missing items in the config.",
            ) from error

        return yaml_data
