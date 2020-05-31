# -*- coding: utf-8 -*-

import contextlib
import os
from pathlib import Path
from typing import Optional

import click
from structlog import get_logger

log = get_logger()


class ConfigStorage(object):
    """Provides methods for storage of config data."""

    def __init__(self, refresh_token_file: str) -> None:
        """Initialize ConfigStorage."""
        self.refresh_token_file = refresh_token_file

    def save_refresh_token(self, refresh_token: Optional[str]) -> None:
        """
        Save the refresh token to a file.

        Create the directory if not exist.
        """
        if not refresh_token:
            return

        Path(os.path.dirname(self.refresh_token_file)).mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(self.refresh_token_file, "w") as token_file:
            token_file.write(refresh_token)

        log.info("refresh_token_save", path=self.refresh_token_file)
        click.echo("The 'refresh token' has been stored to: {0}".format(
            self.refresh_token_file,
        ))

    def load_refresh_token(self) -> Optional[str]:
        """Load the refresh token from a file if exists."""
        try:
            with open(self.refresh_token_file) as token_file:
                log.info("refresh_token_load", path=self.refresh_token_file)
                return token_file.read()
        except IOError:
            log.info("refresh_token_missing", path=self.refresh_token_file)
            return None

    def delete_refresh_token(self) -> None:
        """Delete the refresh token file."""
        with contextlib.suppress(FileNotFoundError):
            log.info("refresh_token_delete", path=self.refresh_token_file)
            os.remove(self.refresh_token_file)
