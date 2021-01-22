# -*- coding: utf-8 -*-

import re
from string import Template

import click
from praw import Reddit
from structlog import get_logger

from slow_start_rewatch.config import Config
from slow_start_rewatch.exceptions import (
    ImageNotFound,
    PostConversionError,
    RedditError,
)
from slow_start_rewatch.post import Post
from slow_start_rewatch.reddit.text_post_converter import TextPostConverter
from slow_start_rewatch.schedule.schedule import Schedule

log = get_logger()


class PostHelper(object):
    """Provides methods for preparing Post content."""

    def __init__(
        self,
        config: Config,
        reddit: Reddit,
    ) -> None:
        """Initialize PostHelper."""
        self.reddit = reddit
        self.post_converter = TextPostConverter(config, reddit)

    def prepare_post(
        self,
        post: Post,
        schedule: Schedule,
        prepare_thumbnail=False,
    ) -> None:
        """
        Prepare the post body based on the post body template.

        Substitute placeholders using the attributes of the provided `Schedule`
        instance.

        Call :meth:`prepare_thumbnail()` if :attr:`Post.submit_with_thumbnail`
        is `True`.
        """
        mapping = {}

        for schedule_post in schedule.posts:
            if schedule_post.name == post.name:
                navigation_text = schedule_post.navigation_current
            elif schedule_post.submission_id:
                navigation_text = re.sub(
                    r"\$link",
                    "/{0}".format(schedule_post.submission_id),
                    schedule_post.navigation_submitted,
                )
            else:
                navigation_text = schedule_post.navigation_scheduled

            mapping[schedule_post.name] = navigation_text

        post.body_md = Template(post.body_template).safe_substitute(
            mapping,
        )

        if prepare_thumbnail and post.submit_with_thumbnail:
            self.prepare_thumbnail(post)

    def prepare_thumbnail(self, post: Post) -> None:
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
