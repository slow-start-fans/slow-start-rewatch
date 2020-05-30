# -*- coding: utf-8 -*-

from unittest.mock import call, patch

import pytest
from prawcore.exceptions import PrawcoreException

from slow_start_rewatch.exceptions import AuthorizationError, RedditError
from slow_start_rewatch.http_server import http_server
from slow_start_rewatch.reddit.oauth_helper import OAuthHelper
from tests.conftest import (
    HTTP_SERVER_HOSTNAME,
    HTTP_SERVER_PORT,
    OAUTH_CODE,
    MockConfig,
)


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

    oauth_helper.authorize()

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


@pytest.fixture()
def oauth_helper_config():
    """Return mock Config for testing OAuthHelper."""
    return MockConfig({
        "reddit": {"oauth_scope": ["headpat", "hug"]},
        "http_server": {
            "hostname": HTTP_SERVER_HOSTNAME,
            "port": HTTP_SERVER_PORT,
        },
    })
