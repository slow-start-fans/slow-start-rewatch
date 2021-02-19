# -*- coding: utf-8 -*-

import re
import textwrap

import click
from praw import Reddit
from prawcore.exceptions import Forbidden, NotFound, PrawcoreException
from structlog import get_logger

from slow_start_rewatch.config import Config
from slow_start_rewatch.exceptions import (
    InvalidWikiLink,
    MissingPost,
    MissingSchedule,
    RedditError,
)
from slow_start_rewatch.schedule.schedule_storage import ScheduleStorage

log = get_logger()


class ScheduleWikiStorage(ScheduleStorage):
    """Stores data about scheduled posts in Reddit wiki."""

    def __init__(
        self,
        config: Config,
        reddit: Reddit,
    ) -> None:
        """Initialize ScheduleWikiStorage."""
        super().__init__()

        self.reddit = reddit

        schedule_wiki_url: str = config["schedule_wiki_url"]

        if not schedule_wiki_url:
            raise RuntimeError(
                "The config must contain 'schedule_wiki_url' item.",
            )

        match = re.search(
            r"\/r\/(?P<subreddit>[^\/]+)\/wiki\/(?P<path>.+)",
            schedule_wiki_url,
        )

        if not match:
            raise InvalidWikiLink(
                "The link to the schedule wiki page is invalid: {0}".format(
                    schedule_wiki_url,
                ),
            )

        self.wiki_path = match.group("path")
        self.wiki_subreddit = match.group("subreddit")

        self.wiki = self.reddit.subreddit(self.wiki_subreddit).wiki

    def load_schedule_data(self) -> str:
        """Load schedule data from the wiki."""
        log.info(
            "schedule_wiki_read",
            subreddit=self.wiki_subreddit,
            wiki_path=self.wiki_path,
        )
        click.echo(
            click.style(
                "Loading the schedule from: /r/{0}/wiki/{1}".format(
                    self.wiki_subreddit,
                    self.wiki_path,
                ),
                fg="cyan",
            ),
        )

        try:
            schedule_data = self.wiki[self.wiki_path].content_md
        except NotFound as error:
            log.exception("schedule_wiki_missing")
            raise MissingSchedule(
                "The schedule wiki page not found: /r/{0}/wiki/{1}".format(
                    self.wiki_subreddit,
                    self.wiki_path,
                ),
            ) from error
        except Forbidden as error:
            log.exception("schedule_wiki_access_denied")
            raise MissingSchedule(
                "Missing permissions to access the schedule wiki page: " +
                "/r/{0}/wiki/{1}".format(
                    self.wiki_subreddit,
                    self.wiki_path,
                ),
            ) from error

        return schedule_data

    def load_post_body(self, body_template_source: str) -> str:
        """Load a post body from the wiki."""
        wiki_path = "{0}/{1}".format(
            self.wiki_path,
            body_template_source,
        )
        log.info(
            "post_wiki_read",
            subreddit=self.wiki_subreddit,
            wiki_path=wiki_path,
        )
        click.echo(
            click.style(
                "Loading the post from: /r/{0}/wiki/{1}".format(
                    self.wiki_subreddit,
                    wiki_path,
                ),
                fg="cyan",
            ),
        )

        try:
            post_body = self.wiki[wiki_path].content_md
        except NotFound as error:
            log.exception("post_wiki_missing")
            raise MissingPost(
                "The post wiki page not found: /r/{0}/wiki/{1}".format(
                    self.wiki_subreddit,
                    wiki_path,
                ),
            ) from error
        except Forbidden as error:
            log.exception("post_wiki_access_denied")
            raise MissingPost(
                "Missing permissions to access the post wiki page: " +
                "/r/{0}/wiki/{1}".format(
                    self.wiki_subreddit,
                    wiki_path,
                ),
            ) from error

        return post_body

    def save_schedule_data(self, schedule_data: str) -> None:
        """
        Save the schedule data to the wiki.

        The content is indented by 4 spaces for better formatting on Reddit.
        """
        log.info(
            "schedule_wiki_update",
            subreddit=self.wiki_subreddit,
            wiki_path=self.wiki_path,
        )
        schedule_data = textwrap.indent(text=schedule_data, prefix="    ")

        try:
            self.wiki[self.wiki_path].edit(
                content=schedule_data,
                reason="Rewatch Update",
            )
        except (PrawcoreException, KeyError) as error:
            log.exception("schedule_wiki_update_failed")
            raise RedditError(
                "Failed to update the schedule wiki page: " +
                "/r/{0}/wiki/{1} Error: {2}".format(
                    self.wiki_subreddit,
                    self.wiki_path,
                    str(error),
                ),
            ) from error
