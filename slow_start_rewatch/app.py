# -*- coding: utf-8 -*-

import click

from slow_start_rewatch.config import Config
from slow_start_rewatch.scheduler import Scheduler


class App(object):
    """The main application object."""

    def __init__(self, config: Config) -> None:
        """Initialize App."""
        self.config = config
        self.scheduler = Scheduler(config)

    def run(self) -> None:
        """Runs the application."""
        self.prepare()
        self.start()

    def prepare(self) -> None:
        """
        Make the preparations for the main run.

        - Load the scheduled Post.
        """
        self.scheduler.load(self.config["username"])

    def start(self) -> None:
        """Start the main run."""
        post = self.scheduler.scheduled_post

        if post is None:
            raise RuntimeError(
                "Cannot start the countdown without the scheduled post.",
            )

        click.echo("A post to be submitted: {0} - {1}".format(
            post.subreddit,
            post.title,
        ))
