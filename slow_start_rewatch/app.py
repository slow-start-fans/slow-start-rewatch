# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Optional

import click

from slow_start_rewatch.config import Config
from slow_start_rewatch.reddit.reddit_cutifier import RedditCutifier
from slow_start_rewatch.schedule.scheduler import Scheduler
from slow_start_rewatch.timer import Timer

FG_VALUES = "bright_blue"


class App(object):
    """The main application object."""

    def __init__(
        self,
        schedule_wiki_url: Optional[str] = None,
        schedule_file: Optional[str] = None,
    ) -> None:
        """Initialize App."""
        config = Config()
        config.load()

        if schedule_wiki_url:
            config["schedule_wiki_url"] = schedule_wiki_url
            config["schedule_file"] = None
        elif schedule_file:
            config["schedule_file"] = schedule_file
            config["schedule_wiki_url"] = None

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
            click.style(self.reddit_cutifier.username, fg=FG_VALUES),
        ))

        self.scheduler.load()

    def start(self) -> None:
        """
        Start the main run.

        1. Wait until the scheduled time.

        2. Submit the Post.
        """
        for post in self.scheduler.get_scheduled_posts():
            click.echo((
                "Loaded the next scheduled post:\n" +
                "- Time: {datetime}\n" +
                "- Subreddit: {subreddit}\n" +
                "- Title: {title}\n"
            ).format(
                datetime=click.style(str(post.submit_at), fg=FG_VALUES),
                subreddit=click.style(post.subreddit, fg=FG_VALUES),
                title=click.style(post.title, fg=FG_VALUES),
            ))
            self.timer.wait(post.submit_at)

            click.echo("{0}: Submitting post: {1} - {2}".format(
                datetime.utcnow(),
                post.subreddit,
                post.title,
            ))
            self.reddit_cutifier.submit_post(post)

            self.scheduler.save_schedule()

            self.reddit_cutifier.update_posts(
                self.scheduler.get_submitted_posts(skip_post=post),
            )
