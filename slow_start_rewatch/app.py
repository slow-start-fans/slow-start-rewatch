# -*- coding: utf-8 -*-

from datetime import datetime

import click

from slow_start_rewatch.config import Config
from slow_start_rewatch.reddit.reddit_cutifier import RedditCutifier
from slow_start_rewatch.scheduler import Scheduler
from slow_start_rewatch.timer import Timer


class App(object):
    """The main application object."""

    def __init__(self, config: Config) -> None:
        """Initialize App."""
        self.reddit_cutifier = RedditCutifier(config)
        self.timer = Timer(config)
        self.scheduler = Scheduler(config, self.reddit_cutifier.reddit)

    def run(self) -> None:
        """Runs the application."""
        self.prepare()
        self.start()

    def prepare(self) -> None:
        """
        Make the preparations for the main run.

        1. Authorize as a Reddit user.

        2. Load the scheduled Post.
        """
        self.reddit_cutifier.authorize()

        click.echo("Logged in as: {0}".format(
            click.style(self.reddit_cutifier.username, fg="bright_blue"),
        ))

        self.scheduler.load()

    def start(self) -> None:
        """
        Start the main run.

        1. Wait until the scheduled time.

        2. Submit the Post.
        """
        post = self.scheduler.scheduled_post

        if post is None:
            raise RuntimeError(
                "Cannot start the countdown without the scheduled post.",
            )

        self.timer.wait(post.submit_at)

        click.echo("{0}: Submitting post: {1} - {2}".format(
            datetime.now(),
            post.subreddit,
            post.title,
        ))
        self.reddit_cutifier.submit_post(post)
