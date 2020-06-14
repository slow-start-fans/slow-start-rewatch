# -*- coding: utf-8 -*-

import os
from datetime import datetime, timedelta
from string import Template
from typing import Optional

import click
from praw import Reddit
from ruamel.yaml import YAML, YAMLError  # type: ignore
from structlog import get_logger

from slow_start_rewatch.config import ROOT_DIR, Config
from slow_start_rewatch.exceptions import (
    EmptySchedule,
    ImageNotFound,
    InvalidSchedule,
    MissingSchedule,
    PostConversionError,
    RedditError,
)
from slow_start_rewatch.post import Post
from slow_start_rewatch.reddit.text_post_converter import TextPostConverter

DEFAULT_SCHEDULED_POST_FILE = os.path.join(
    ROOT_DIR,
    "templates",
    "scheduled_post.yml",
)
DEFAULT_DELAY = 5

log = get_logger()


class Scheduler(object):
    """Manages data about scheduled posts."""

    def __init__(
        self,
        config: Config,
        reddit: Reddit,
    ) -> None:
        """Initialize Scheduler."""
        self.scheduled_post_file: str = config["scheduled_post_file"]
        self.scheduled_post: Optional[Post] = None
        self.reddit = reddit
        self.post_converter = TextPostConverter(config, reddit)

    def load(self) -> None:
        """
        Load a scheduled post from a file.

        If the file doesn't exist and empty sample is created.
        """
        log.debug("scheduled_post_load", path=self.scheduled_post_file)

        try:
            post = self.parse_post_from_yaml(self.scheduled_post_file)
        except FileNotFoundError:
            log.warning("scheduled_post_missing")
            self.create_default()
            raise MissingSchedule(
                "The scheduled post file not found.",
                hint="Created a sample in: {0}".format(
                    self.scheduled_post_file,
                ),
            )

        if datetime.now() > post.submit_at:
            log.warning(
                "scheduled_post_past_date",
                target_time=post.submit_at,
            )
            raise EmptySchedule(
                "The post was scheduled in the past: {0}".format(
                    post.submit_at,
                ),
                hint="Please adjust the scheduled time.",
            )

        if post.submit_with_thumbnail:
            self.prepare_post(post)

        self.scheduled_post = post

        click.echo((
            "Loaded the scheduled post:\n" +
            "- Time: {datetime}\n" +
            "- Subreddit: {subreddit}\n" +
            "- Title: {title}\n"
        ).format(
            datetime=click.style(str(post.submit_at), fg="bright_blue"),
            subreddit=click.style(post.subreddit, fg="bright_blue"),
            title=click.style(post.title, fg="bright_blue"),
        ))

    def parse_post_from_yaml(self, path: str) -> Post:
        """Parse the scheduled post from YAML."""
        yaml = YAML(typ="safe")

        with open(path) as post_file:
            yaml_content = post_file.read()

        try:
            yaml_data = yaml.load(yaml_content)
        except (YAMLError, AttributeError) as yaml_error:
            log.exception("scheduled_post_invalid")
            raise InvalidSchedule(
                "Failed to parse the data about the scheduled post.",
                hint="Repair the structure of the scheduled post file.",
            ) from yaml_error

        try:
            post = Post(
                submit_at=yaml_data["submit_at"],
                subreddit=yaml_data["subreddit"],
                title=yaml_data["title"],
                body_md=yaml_data["body"],
                submit_with_thumbnail=yaml_data.get(
                    "submit_with_thumbnail",
                    True,
                ),
            )
        except (AttributeError, KeyError) as missing_data_error:
            log.exception("scheduled_post_incomplete")
            raise InvalidSchedule(
                "Incomplete scheduled post data.",
                hint="Make sure all the fields are filled in.",
            ) from missing_data_error

        return post

    def create_default(self) -> None:
        """
        Create a sample scheduled post.

        The profile of the user is used as a subreddit which could be used for
        testing. The scheduled time is set 5 minutes from the current time.
        """
        with open(DEFAULT_SCHEDULED_POST_FILE) as default_post_file:
            yaml_template = Template(default_post_file.read())

        post_attributes = {
            "submit_at": (
                datetime.now() + timedelta(minutes=DEFAULT_DELAY)
            ).isoformat(" ", "seconds"),
            "subreddit": "u_{0}".format(self.reddit.user.me().name),
        }

        yaml_content = yaml_template.substitute(post_attributes)

        log.info(
            "scheduled_post_create_default",
            submit_at=post_attributes["submit_at"],
            subreddit=post_attributes["subreddit"],
            path=self.scheduled_post_file,
        )

        with open(self.scheduled_post_file, "w") as sample_post_file:
            sample_post_file.write(yaml_content)

    def prepare_post(self, post: Post) -> None:
        """
        Prepare the post for the submission with thumbnail.

        Converted the post to the Rich Text JSON format so that Reddit creates
        a thumbnail for the post.
        """
        log.debug("scheduled_post_convert")
        try:
            post.body_rtjson = self.post_converter.convert_to_rtjson(
                post.body_md,
            )
        except ImageNotFound:
            log.warning("scheduled_post_missing_image", post=str(post))
            post.submit_with_thumbnail = False
            click.echo(click.style(
                "Warning: No image found in the post.\n" +
                "To submit a post without image set the " +
                "'submit_with_thumbnail' option to False.",
                fg="red",
            ))
        except (RedditError, PostConversionError) as exception:
            log.exception("scheduled_post_convert_error")
            exception.hint = (
                "To avoid further issues you can submit a post without " +
                "image by setting the 'submit_with_thumbnail' option to False."
            )
            raise
