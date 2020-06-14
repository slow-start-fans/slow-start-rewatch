# -*- coding: utf-8 -*-

import time

from praw import Reddit
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
            refresh_token=config.refresh_token,
        )

        self.oauth_helper = OAuthHelper(config, self.reddit)
        self.reddit_helper = RedditHelper(config, self.reddit)

        self.post_update_delay = config[
            "reddit_cutifier.post_update_delay"
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

    def submit_post(self, post: Post) -> str:
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
                )
            else:
                submission = self.reddit.subreddit(
                    post.subreddit,
                ).submit(
                    title=post.title,
                    selftext=post.body_md,
                )
        except PrawcoreException as exception:
            log.exception("post_submit_error")
            raise RedditError(
                "Failed to submit the post.",
            ) from exception

        log.debug("post_submit_result", permalink=submission.permalink)

        submission = self.update_post(submission, post)

        return submission.permalink

    def update_post(self, submission: Submission, post: Post) -> Submission:
        """Replace the content of the Submission with the Post Markdown."""
        if not post.submit_with_thumbnail:
            return submission

        delay = self.post_update_delay
        log.debug("post_update_delay", delay=delay)
        time.sleep(delay / 1000)

        log.info("post_update", post=str(post), submission=submission.id)
        try:
            return submission.edit(post.body_md)
        except PrawcoreException as exception:
            log.exception("post_update_error")
            raise RedditError(
                "Failed to update the post.",
            ) from exception
