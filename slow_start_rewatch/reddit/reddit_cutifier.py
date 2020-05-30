# -*- coding: utf-8 -*-

from praw import Reddit
from structlog import get_logger

from slow_start_rewatch.config import Config
from slow_start_rewatch.reddit.oauth_helper import OAuthHelper

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

    @property
    def username(self) -> str:
        """Get username."""
        if not self.reddit.user.me():
            raise AttributeError("Cannot get the username before authorizing.")

        return self.reddit.user.me().name

    def authorize(self) -> None:
        """Authorize user using the :class:`.OAuthHelper`."""
        self.oauth_helper.authorize()
