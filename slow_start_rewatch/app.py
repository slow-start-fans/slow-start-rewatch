# -*- coding: utf-8 -*-

import click

from slow_start_rewatch.config import Config


class App(object):
    """The main application object."""

    def __init__(self, config: Config) -> None:
        """Initialize App."""
        self.config = config

    def run(self) -> None:
        """Runs the application."""
        click.echo("Starting the Slow Start Rewatch...")
