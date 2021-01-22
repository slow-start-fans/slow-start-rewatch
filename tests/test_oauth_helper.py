# -*- coding: utf-8 -*-

from unittest.mock import Mock, call, patch

import pytest
from prawcore.exceptions import (
    OAuthException,
    PrawcoreException,
    ResponseException,
)

from slow_start_rewatch.exceptions import (
    AuthorizationError,
    InvalidRefreshToken,
    MissingRefreshToken,
    RedditError,
)
from slow_start_rewatch.http_server import http_server
from slow_start_rewatch.reddit.oauth_helper import OAuthHelper
from tests.conftest import (
    HTTP_SERVER_HOSTNAME,
    HTTP_SERVER_PORT,
    OAUTH_CODE,
    REFRESH_TOKEN,
    MockConfig,
)


def test_valid_token(oauth_helper_config, reddit):
    """Test the authorization with a valid token."""
    oauth_helper_config["refresh_token"] = REFRESH_TOKEN
    oauth_helper = OAuthHelper(oauth_helper_config, reddit)

    oauth_helper.authorize()

    assert reddit.auth.scopes.call_count == 1


@patch.object(OAuthHelper, "validate_refresh_token")
@patch.object(OAuthHelper, "authorize_via_oauth")
def test_missing_token(
    mock_authorize_via_oauth,
    mock_validate_refresh_token,
    oauth_helper_config,
    reddit,
):
    """Test the authorization when a token is missing."""
    oauth_helper = OAuthHelper(oauth_helper_config, reddit)

    with pytest.raises(MissingRefreshToken):
        oauth_helper.authorize_via_token()

    oauth_helper.authorize()
    assert mock_authorize_via_oauth.call_count == 1
    assert mock_validate_refresh_token.call_count == 0


@patch.object(OAuthHelper, "authorize_via_oauth")
def test_invalid_token(mock_authorize_via_oauth, oauth_helper_config, reddit):
    """Test the authorization with an invalid token."""
    response = Mock()
    response.status_code = 400
    reddit.auth.scopes.side_effect = ResponseException(response)

    oauth_helper_config["refresh_token"] = REFRESH_TOKEN
    oauth_helper = OAuthHelper(oauth_helper_config, reddit)

    oauth_helper.authorize()

    assert reddit.auth.scopes.call_count == 1
    assert mock_authorize_via_oauth.call_count == 1
    assert oauth_helper.config["refresh_token"] is None

    oauth_helper.config["refresh_token"] = REFRESH_TOKEN

    with pytest.raises(InvalidRefreshToken):
        oauth_helper.authorize_via_token()


@patch.object(OAuthHelper, "authorize_via_oauth")
def test_failed_token_validation(
    mock_authorize_via_oauth,
    oauth_helper_config,
    reddit,
):
    """Test errors during the token validation."""
    response = Mock()
    response.status_code = 500
    reddit.auth.scopes.side_effect = [
        ResponseException(response),
        OAuthException(response, 500, "The server is pouting"),
        None,
    ]

    oauth_helper_config["refresh_token"] = REFRESH_TOKEN
    oauth_helper = OAuthHelper(oauth_helper_config, reddit)
    with pytest.raises(RedditError):
        oauth_helper.authorize()

    with pytest.raises(RedditError):
        oauth_helper.authorize()

    assert mock_authorize_via_oauth.call_count == 0

    oauth_helper.authorize()

    assert mock_authorize_via_oauth.call_count == 1


@patch.object(http_server, "run")
@patch("webbrowser.open_new")
def test_successful_authorization(
    webbrowser_open_new,
    http_server_run,
    oauth_helper_config,
    reddit,
):
    """Test successful OAuth authorization."""
    http_server_run.return_value = OAUTH_CODE

    oauth_helper = OAuthHelper(oauth_helper_config, reddit)

    assert oauth_helper.config["refresh_token"] is None

    oauth_helper.authorize()

    assert oauth_helper.config["refresh_token"] == REFRESH_TOKEN
    assert webbrowser_open_new.call_count == 1
    assert reddit.auth.authorize.call_args == call(OAUTH_CODE)


@patch.object(http_server, "run")
@patch("webbrowser.open_new")
def test_failed_authorization(
    webbrowser_open_new,
    http_server_run,
    oauth_helper_config,
    reddit,
):
    """Test an error during OAuth authorization."""
    http_server_run.side_effect = AuthorizationError("Tsundere response")

    oauth_helper = OAuthHelper(oauth_helper_config, reddit)

    with pytest.raises(AuthorizationError):
        oauth_helper.authorize()

    assert oauth_helper.config["refresh_token"] is None


@patch.object(http_server, "run")
@patch("webbrowser.open_new")
def test_failed_token_retrieval(
    webbrowser_open_new,
    http_server_run,
    oauth_helper_config,
    reddit,
):
    """Test errors during the refresh token retrieval."""
    http_server_run.return_value = OAUTH_CODE
    reddit.auth.authorize.side_effect = [
        PrawcoreException,
        None,
    ]

    oauth_helper = OAuthHelper(oauth_helper_config, reddit)

    with pytest.raises(RedditError):
        oauth_helper.authorize()

    with pytest.raises(AuthorizationError):
        oauth_helper.authorize()

    assert oauth_helper.config["refresh_token"] is None


@pytest.fixture()
def oauth_helper_config():
    """Return mock Config for testing OAuthHelper."""
    return MockConfig({
        "reddit": {"oauth_scope": ["headpat", "hug"]},
        "http_server": {
            "hostname": HTTP_SERVER_HOSTNAME,
            "port": HTTP_SERVER_PORT,
        },
        "refresh_token": None,
    })
