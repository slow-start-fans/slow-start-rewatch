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
        self.prepare()
        self.start()

    def prepare(self) -> None:
        """Make the preparations for the main run."""
        click.echo("Preparing the Slow Start Rewatch...")

    def start(self) -> None:
        """Start the main run."""
        click.echo("Starting the Slow Start Rewatch...")
