# -*- coding: utf-8 -*-

import uuid
import webbrowser

import click
from praw import Reddit
from prawcore.exceptions import (
    OAuthException,
    PrawcoreException,
    ResponseException,
)
from structlog import get_logger

from slow_start_rewatch.config import Config
from slow_start_rewatch.exceptions import (
    AuthorizationError,
    InvalidRefreshToken,
    MissingRefreshToken,
    RedditError,
)
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
        Authorize the user.

        1. Try to authorize using the stored refresh token.

        2. If the refresh token is missing or invalid, authorize via OAuth.
        """
        try:
            self.authorize_via_token()
        except (MissingRefreshToken, InvalidRefreshToken) as exception:
            click.echo(str(exception))
            self.authorize_via_oauth()

    def authorize_via_token(self) -> None:
        """Authorize via the refresh token if the token exists."""
        if not self.config["refresh_token"]:
            log.warning("refresh_token_missing")
            raise MissingRefreshToken

        self.validate_refresh_token()

    def validate_refresh_token(self) -> None:
        """
        Validate the refresh token.

        The validation is performed by sending a request to the Reddit API.

        The refresh token must be set when :class:`praw.Reddit` is initialized.
        """
        log.info("refresh_token_validate")
        try:
            scopes = self.reddit.auth.scopes()
        except ResponseException as exception:
            if exception.response.status_code == BAD_REQUEST_ERROR:
                # Reddit throws a generic 400 error when the refresh token is
                # not accepted.
                self.config["refresh_token"] = None
                log.error("refresh_token_invalid")
                raise InvalidRefreshToken(
                    "Cannot log in with the stored refresh token. " +
                    "The token has been removed.",
                )

            log.exception("refresh_token_validation_error")
            raise RedditError(
                "Reddit error when validating refresh token.",
            ) from exception
        except OAuthException as exception:
            log.exception("refresh_token_validation_error")
            raise RedditError(
                "Reddit OAuth error when validating refresh token.",
            ) from exception

        if not scopes:
            log.error("refresh_token_validation_failed")
            raise InvalidRefreshToken("Failed to validate the refresh token.")

    def authorize_via_oauth(self) -> None:
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
            "- To maintain access the app will store a 'refresh token' " +
            "to your home directory.\n" +
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

        self.config["refresh_token"] = refresh_token
