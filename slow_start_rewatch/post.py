# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Optional

from structlog import get_logger

from slow_start_rewatch.reddit.reddit_helper import RichTextJson

log = get_logger()


class Post(object):  # noqa: WPS230
    """Represents a scheduled Reddit post."""

    def __init__(  # noqa: WPS211
        self,
        name: str,
        submit_at: datetime,
        subreddit: str,
        title: str,
        body_template: str,
        submit_with_thumbnail=True,
        flair_id=None,
        navigation_submitted=None,
        navigation_current=None,
        navigation_scheduled=None,
        submission_id=None,
    ) -> None:
        """Initialize Post."""
        log.info(
            "post_create",
            submit_at=str(submit_at),
            subreddit=subreddit,
            title=title,
            submit_with_thumbnail=submit_with_thumbnail,
        )

        if not all([name, submit_at, subreddit, title, body_template]):
            raise AttributeError("Missing required post fields.")

        self.name = name
        self.submit_at = submit_at
        self.subreddit = subreddit
        self.title = title
        self.body_template = body_template
        self.submit_with_thumbnail = submit_with_thumbnail
        self.navigation_submitted: str = navigation_submitted or "$link"
        self.flair_id: Optional[str] = flair_id
        self.navigation_current: str = navigation_current or ""
        self.navigation_scheduled: str = navigation_scheduled or ""
        self.submission_id: Optional[str] = submission_id

        self.body_md: Optional[str] = None
        self.body_rtjson: Optional[RichTextJson] = None

    def __eq__(self, other: object) -> bool:
        """Compare this instance to other object."""
        if not isinstance(other, self.__class__):
            return NotImplemented

        return (
            self.name,
            self.submit_at,
            self.subreddit,
            self.title,
            self.body_template,
        ) == (
            other.name,
            other.submit_at,
            other.subreddit,
            other.title,
            other.body_template,
        )

    def __str__(self):
        """Return string representation of this instance."""
        return "/r/{subreddit} Post at {datetime}: {title}".format(
            subreddit=self.subreddit,
            datetime=self.submit_at,
            title=self.title,
        )
