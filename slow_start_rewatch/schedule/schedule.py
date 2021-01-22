# -*- coding: utf-8 -*-

from typing import List, Optional

from structlog import get_logger

from slow_start_rewatch.post import Post

log = get_logger()


class Schedule(object):
    """Represents scheduled Reddit posts."""

    def __init__(  # noqa: WPS211
        self,
        subreddit: str,
        posts: Optional[List[Post]] = None,
    ) -> None:
        """Initialize Schedule."""
        log.info(
            "schedule_create",
            subreddit=subreddit,
        )

        if not subreddit:
            raise AttributeError("'subreddit' field must be set.")

        self.subreddit = subreddit
        self.posts = posts or []

    def __eq__(self, other: object) -> bool:
        """Compare this instance to other object."""
        if not isinstance(other, self.__class__):
            return NotImplemented

        if self.subreddit != other.subreddit:
            return False

        if len(self.posts) != len(other.posts):
            return False

        for index, post in enumerate(self.posts):
            if post != other.posts[index]:
                return False

        return True
