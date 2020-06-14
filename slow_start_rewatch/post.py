# -*- coding: utf-8 -*-

from datetime import datetime

from structlog import get_logger

log = get_logger()


class Post(object):
    """Represents a scheduled Reddit post."""

    def __init__(
        self,
        submit_at: datetime,
        subreddit: str,
        title: str,
        body: str,
    ) -> None:
        """Initialize Post."""
        log.info(
            "post_create",
            submit_at=str(submit_at),
            subreddit=subreddit,
            title=title,
        )

        if not all([submit_at, subreddit, title, body]):
            raise AttributeError("All Post fields must be set.")

        self.submit_at = submit_at
        self.subreddit = subreddit
        self.title = title
        self.body = body

    def __eq__(self, other: object) -> bool:
        """Compare this instance to other object."""
        if not isinstance(other, self.__class__):
            return NotImplemented

        return (
            self.submit_at,
            self.subreddit,
            self.title,
            self.body,
        ) == (
            other.submit_at,
            other.subreddit,
            other.title,
            other.body,
        )

    def __str__(self):
        """Return string representation of this instance."""
        return "/r/{subreddit} Post at {datetime}: {title}".format(
            subreddit=self.subreddit,
            datetime=self.submit_at,
            title=self.title,
        )
