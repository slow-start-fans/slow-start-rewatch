# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from datetime import datetime
from io import StringIO
from typing import Dict, List, Union

from ruamel.yaml import YAML, YAMLError  # type: ignore
from structlog import get_logger

from slow_start_rewatch.exceptions import InvalidSchedule
from slow_start_rewatch.post import Post
from slow_start_rewatch.schedule.schedule import Schedule

log = get_logger()

# Type alias for posts YAML data.
PostsData = List[
    Dict[str, Union[str, datetime, bool, None]]
]


class ScheduleStorage(ABC):
    """Stores data about scheduled posts."""

    def load(self) -> Schedule:
        """Parse and load the schedule."""
        yaml = YAML(typ="safe")
        schedule_data = self.load_schedule_data()

        try:
            yaml_data = yaml.load(schedule_data)
        except (YAMLError, AttributeError) as yaml_error:
            log.exception("schedule_invalid")
            raise InvalidSchedule(
                "Failed to parse the data about the schedule.",
                hint="Repair the structure of the schedule file.",
            ) from yaml_error

        try:
            schedule = Schedule(
                subreddit=yaml_data["subreddit"],
                posts=self.load_posts(
                    yaml_data["posts"],
                    yaml_data["subreddit"],
                ),
            )
        except (AttributeError, KeyError) as missing_data_error:
            log.exception("schedule_incomplete")
            raise InvalidSchedule(
                "Incomplete schedule data.",
                hint="Make sure all the fields are filled in.",
            ) from missing_data_error

        return schedule

    @abstractmethod
    def load_schedule_data(self) -> str:
        """Load schedule data from the storage."""

    def load_posts(
        self,
        posts_data: PostsData,
        subreddit: str,
    ) -> List[Post]:
        """Parse and load scheduled posts."""
        posts = []

        for post_data in posts_data:
            if not isinstance(post_data["submit_at"], datetime):
                log.exception("schedule_incomplete")
                raise InvalidSchedule(
                    (
                        "The 'submit_at' field of the scheduled post '{0}' " +
                        "contains an invalid value."
                    ).format(
                        post_data["name"],
                    ),
                    hint="All dates must be in 'YYYY-MM-DD hh:mm:ss' format.",
                )

            post_body = self.load_post_body(
                str(post_data["body_template"]),
            )

            post = Post(
                name=str(post_data["name"]),
                submit_at=post_data["submit_at"],
                subreddit=subreddit,
                title=str(post_data["title"]),
                body_template=post_body,
                submit_with_thumbnail=post_data.get(
                    "submit_with_thumbnail",
                    True,
                ),
                flair_id=post_data.get("flair_id"),
                navigation_submitted=post_data.get("navigation_submitted"),
                navigation_current=post_data.get("navigation_current"),
                navigation_scheduled=post_data.get("navigation_scheduled"),
                submission_id=post_data.get("submission_id"),
            )

            posts.append(post)

        return posts

    @abstractmethod
    def load_post_body(self, body_template_source: str) -> str:
        """Load a post body from the storage."""

    def save(self, schedule: Schedule) -> None:
        """
        Save the Schedule.

        1. Load the Schedule data.

        2. Populate the Schedule Data with the post IDs of submitted posts.

        3. Save the Schedule data.
        """
        yaml_content = self.load_schedule_data()

        yaml = YAML(typ="safe")
        yaml.default_flow_style = False
        yaml.sort_base_mapping_type_on_output = False

        yaml_data = yaml.load(yaml_content)

        yaml_data["posts"] = self.update_submitted_posts(
            yaml_data["posts"],
            schedule,
        )

        string_stream = StringIO()

        yaml.dump(yaml_data, string_stream)

        schedule_data = string_stream.getvalue()
        string_stream.close()

        self.save_schedule_data(schedule_data)

    def update_submitted_posts(
        self,
        posts_data: PostsData,
        schedule: Schedule,
    ) -> PostsData:
        """Populate the data with IDs of submitted posts."""
        submission_ids = {
            post.name: post.submission_id
            for post in schedule.posts
        }

        for index, post_data in enumerate(posts_data):
            post_name = str(post_data.get("name"))
            submission_id = submission_ids.get(post_name)

            if submission_id:
                posts_data[index]["submission_id"] = submission_id

        return posts_data

    @abstractmethod
    def save_schedule_data(self, schedule_data: str) -> None:
        """Save schedule data to the storage."""
