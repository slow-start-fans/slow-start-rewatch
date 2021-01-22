# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Iterator, List, Optional

from praw import Reddit
from structlog import get_logger

from slow_start_rewatch.config import Config
from slow_start_rewatch.exceptions import MissingSchedule
from slow_start_rewatch.post import Post
from slow_start_rewatch.post_helper import PostHelper
from slow_start_rewatch.schedule.schedule import Schedule
from slow_start_rewatch.schedule.schedule_file_storage import (
    ScheduleFileStorage,
)
from slow_start_rewatch.schedule.schedule_storage import ScheduleStorage
from slow_start_rewatch.schedule.schedule_wiki_storage import (
    ScheduleWikiStorage,
)

log = get_logger()


class Scheduler(object):
    """Manages data about scheduled posts."""

    def __init__(
        self,
        config: Config,
        reddit: Reddit,
    ) -> None:
        """Initialize Scheduler."""
        self.schedule: Optional[Schedule] = None
        self.reddit = reddit
        self.post_helper = PostHelper(config, reddit)

        self.schedule_storage: ScheduleStorage
        if config["schedule_wiki_url"]:
            self.schedule_storage = ScheduleWikiStorage(config, reddit)
        elif config["schedule_file"]:
            self.schedule_storage = ScheduleFileStorage(config)
        else:
            raise MissingSchedule(
                "Schedule storage not defined.",
                hint="The Schedule must be stored in a file or Reddit's wiki.",
            )

    def load(self) -> None:
        """Load the schedule from the storage."""
        self.schedule = self.schedule_storage.load()

    def get_scheduled_posts(self) -> Iterator[Post]:
        """Provide a generator of the scheduled posts."""
        while True:
            post = self.get_next_post()

            if not post:
                break

            yield post

    def get_next_post(self) -> Optional[Post]:
        """Find, prepare, and return the next scheduled posts."""
        if not self.schedule:
            raise RuntimeError(
                "The Schedule must be loaded before calling this method.",
            )

        current_time = datetime.utcnow()
        log.debug("get_next_post", after_time=current_time)

        for post in self.schedule.posts:
            if not post.submission_id and post.submit_at > current_time:
                next_post = post
                break
        else:
            return None

        self.post_helper.prepare_post(
            post=next_post,
            schedule=self.schedule,
            prepare_thumbnail=True,
        )

        return next_post

    def get_submitted_posts(
        self,
        skip_post: Optional[Post] = None,
    ) -> List[Post]:
        """Return a list of previously submitted posts."""
        if not self.schedule:
            raise RuntimeError(
                "The schedule must be loaded before calling this method.",
            )

        posts = []
        for post in self.schedule.posts:
            if skip_post and post.name == skip_post.name:
                continue

            if post.submission_id:
                self.post_helper.prepare_post(post, self.schedule)
                posts.append(post)

        return posts

    def save_schedule(self) -> None:
        """Save the schedule to the storage."""
        if not self.schedule:
            raise RuntimeError(
                "The schedule must be loaded before calling this method.",
            )

        self.schedule_storage.save(self.schedule)
