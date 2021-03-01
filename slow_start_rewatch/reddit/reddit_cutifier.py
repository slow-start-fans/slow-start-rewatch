# -*- coding: utf-8 -*-

import time
from typing import List, Optional

import click
from praw import Reddit
from praw.exceptions import RedditAPIException
from praw.reddit import Submission
from prawcore.exceptions import PrawcoreException
from structlog import get_logger

from slow_start_rewatch.config import Config
from slow_start_rewatch.exceptions import RedditError
from slow_start_rewatch.post import Post
from slow_start_rewatch.reddit.oauth_helper import OAuthHelper
from slow_start_rewatch.reddit.reddit_helper import RedditHelper

log = get_logger()


class RedditCutifier(object):
    """
    Reddit Cutifier is in charge of making Reddit a cuter place.

    In other words, it provides a set of actions to be executed on Reddit via
    the PRAW package.
    """

    def __init__(self, config: Config) -> None:
        """Initialize RedditCutifier."""
        reddit_config = config["reddit"]
        redirect_uri = "http://{0}:{1}/".format(
            config["http_server.hostname"],
            config["http_server.port"],
        )

        user_agent = reddit_config["user_agent"]
        client_id = reddit_config["client_id"]
        client_secret = reddit_config["client_secret"]

        log.debug(
            "reddit_init",
            user_agent=user_agent,
            client_id=client_id,
            client_secret_set=bool(client_secret),
        )
        self.reddit = Reddit(
            user_agent=user_agent,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            refresh_token=config["refresh_token"],
        )

        self.oauth_helper = OAuthHelper(config, self.reddit)
        self.reddit_helper = RedditHelper(config, self.reddit)

        self.post_update_delay = config[
            "reddit_cutifier.post_update_delay"
        ]
        self.previous_post_update_delay = config[
            "reddit_cutifier.previous_post_update_delay"
        ]

    @property
    def username(self) -> str:
        """Get username."""
        if not self.reddit.user.me():
            raise AttributeError("Cannot get the username before authorizing.")

        return self.reddit.user.me().name

    def authorize(self) -> None:
        """Authorize user using the :class:`.OAuthHelper`."""
        self.oauth_helper.authorize()

    def submit_post(self, post: Post) -> Submission:
        """
        Submit the post to Reddit.

        If the post is set to be submitted with thumbnail, submit its body in
        the Rich Text JSON format. Otherwise submit the Markdown content using
        regular method of `PRAW`.
        """
        log.info("post_submit", post=str(post))
        try:
            if post.submit_with_thumbnail and post.body_rtjson:
                submission = self.reddit_helper.submit_post_rtjson(
                    subreddit=post.subreddit,
                    title=post.title,
                    body_rtjson=post.body_rtjson,
                    flair_id=post.flair_id,
                )
            else:
                submission = self.reddit.subreddit(
                    post.subreddit,
                ).submit(
                    title=post.title,
                    selftext=post.body_md,
                    flair_id=post.flair_id,
                )
        except PrawcoreException as exception:
            log.exception("post_submit_error")
            raise RedditError(
                "Failed to submit the post.",
            ) from exception

        post.submission_id = submission.id

        log.debug("post_submit_result", permalink=submission.permalink)

        if not post.submit_with_thumbnail:
            return submission

        delay = self.post_update_delay
        log.debug("post_update_delay", delay=delay)
        click.echo(
            click.style(
                "Waiting {0}s before updating the post.".format(delay / 1000),
                fg="cyan",
            ),
        )
        time.sleep(delay / 1000)

        return self.update_post(post, submission)

    def update_post(
        self,
        post: Post,
        submission: Optional[Submission] = None,
    ) -> Submission:
        """
        Replace the content of the Submission with the Post Markdown.

        Either `submission` is provided or the `post` must contain the
        `submission_id` attribute.
        """
        if not submission and not post.submission_id:
            raise RuntimeError(
                "Trying to update post '{0}' without 'submission_id'".format(
                    post.name,
                ),
            )
        elif not submission:
            log.info("submission_load", submission=post.submission_id)
            submission = self.reddit.submission(post.submission_id)

        log.info("post_update", post=str(post), submission=submission.id)
        try:
            return submission.edit(post.body_md)
        except (PrawcoreException, RedditAPIException) as error:
            log.exception("post_update_error")
            click.echo(
                click.style(
                    (
                        "Failed to update the post 'https://redd.it/{0}'. " +
                        "Error: {1}"
                    ).format(
                        post.submission_id,
                        str(error),
                    ),
                    fg="red",
                ),
                err=True,
            )

    def update_posts(self, posts: List[Post]) -> None:
        """Update the content of multiple Submissions."""
        log.info("posts_update", post_count=len(posts))

        for post in posts:
            click.echo(
                click.style(
                    "Updating post: {0}".format(post.title),
                    fg="cyan",
                ),
            )

            delay = self.previous_post_update_delay
            log.debug("previous_post_update_delay", delay=delay)
            time.sleep(delay / 1000)

            self.update_post(post)
