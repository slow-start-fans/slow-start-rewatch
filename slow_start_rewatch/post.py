# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Optional

from structlog import get_logger

from slow_start_rewatch.reddit.reddit_helper import RichTextJson

log = get_logger()


class Post(object):
    """Represents a scheduled Reddit post."""

    def __init__(  # noqa: WPS211
        self,
        submit_at: datetime,
        subreddit: str,
        title: str,
        body_md: str,
        submit_with_thumbnail=True,
    ) -> None:
        """Initialize Post."""
        log.info(
            "post_create",
            submit_at=str(submit_at),
            subreddit=subreddit,
            title=title,
            submit_with_thumbnail=submit_with_thumbnail,
        )

        if not all([submit_at, subreddit, title, body_md]):
            raise AttributeError("All Post fields must be set.")

        self.submit_at = submit_at
        self.subreddit = subreddit
        self.title = title
        self.body_md = body_md
        self.submit_with_thumbnail = submit_with_thumbnail
        self.body_rtjson: Optional[RichTextJson] = None

    def __eq__(self, other: object) -> bool:
        """Compare this instance to other object."""
        if not isinstance(other, self.__class__):
            return NotImplemented

        return (
            self.submit_at,
            self.subreddit,
            self.title,
            self.body_md,
        ) == (
            other.submit_at,
            other.subreddit,
            other.title,
            other.body_md,
        )

    def __str__(self):
        """Return string representation of this instance."""
        return "/r/{subreddit} Post at {datetime}: {title}".format(
            subreddit=self.subreddit,
            datetime=self.submit_at,
            title=self.title,
        )
