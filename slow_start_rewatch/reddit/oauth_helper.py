# -*- coding: utf-8 -*-

import uuid
import webbrowser

import click
from praw import Reddit
from prawcore.exceptions import PrawcoreException
from structlog import get_logger

from slow_start_rewatch.config import Config
from slow_start_rewatch.exceptions import AuthorizationError, RedditError
from slow_start_rewatch.http_server import http_server

BAD_REQUEST_ERROR = 400

log = get_logger()


class OAuthHelper(object):
    """Provides methods for Reddit authorization."""

    def __init__(self, config: Config, reddit: Reddit) -> None:
        """Initialize OAuthHelper."""
        self.config = config
        self.reddit = reddit

    def authorize(self) -> None:
        """
        Authorize via OAuth.

        Open a background browser (e.g. firefox) which is non-blocking.

        The server will block until it responds to its first request. Then the
        callback params are checked.
        """
        state = uuid.uuid4().hex
        authorize_url = self.reddit.auth.url(
            scopes=self.config["reddit.oauth_scope"],
            state=state,
        )

        click.echo(
            "Opening a web browser for authorization:\n" +
            "- You will be asked to allow the Slow Start Rewatch app to " +
            "connect with your Reddit account so that it can submit and " +
            "edit posts on your behalf.\n" +
            "- The app cannot access your password.\n" +
            "- Press Ctrl+C if you would like to quit before completing " +
            "the authorization.",
        )
        log.debug("webbrowser_open", url=authorize_url)
        webbrowser.open_new(authorize_url)

        code = http_server.run(
            state=state,
            hostname=self.config["http_server.hostname"],
            port=self.config["http_server.port"],
        )

        log.info("oauth_authorize", code=code)
        try:
            refresh_token = self.reddit.auth.authorize(code)
        except PrawcoreException as exception:
            log.exception("oauth_authorize_failed")
            raise RedditError(
                "Failed to retrieve the Refresh Token.",
            ) from exception

        if not refresh_token:
            log.error("oauth_authorize_missing_token")
            raise AuthorizationError(
                "Reddit hasn't provided the Refresh Token.",
            )
