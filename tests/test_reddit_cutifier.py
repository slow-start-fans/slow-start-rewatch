# -*- coding: utf-8 -*-

from unittest.mock import call, patch

import pytest
from prawcore.exceptions import PrawcoreException

from slow_start_rewatch.exceptions import RedditError
from slow_start_rewatch.reddit.oauth_helper import OAuthHelper
from slow_start_rewatch.reddit.reddit_cutifier import RedditCutifier
from tests.conftest import (
    HTTP_SERVER_HOSTNAME,
    HTTP_SERVER_PORT,
    REFRESH_TOKEN,
    MockConfig,
)


@patch.object(OAuthHelper, "authorize")
@patch("praw.Reddit.__init__", return_value=None)
def test_authorize(
    mock_reddit_init,
    mock_oauth_helper_authorize,
    reddit_cutifier_config,
):
    """
    Test initialization and authorization.

    1. Ensure that the `Reddit` instance is initialized with the correct
       arguments.

    2. Check that the :meth:`OAuthHelper.authorize()` is called during the
       authorization.
    """
    reddit_cutifier_config.refresh_token = REFRESH_TOKEN
    reddit_cutifier = RedditCutifier(reddit_cutifier_config)

    reddit_cutifier.authorize()

    reddit_config = reddit_cutifier_config["reddit"]
    redirect_uri = "http://{0}:{1}/".format(
        reddit_cutifier_config["http_server.hostname"],
        reddit_cutifier_config["http_server.port"],
    )

    expected_call = call(
        user_agent=reddit_config["user_agent"],
        client_id=reddit_config["client_id"],
        client_secret=reddit_config["client_secret"],
        redirect_uri=redirect_uri,
        refresh_token=REFRESH_TOKEN,
    )

    assert mock_reddit_init.call_args == expected_call
    assert mock_oauth_helper_authorize.call_count == 1


@patch.object(OAuthHelper, "authorize")
@patch("praw.Reddit")
def test_username(
    mock_reddit,
    mock_oauth_helper_authorize,
    reddit_cutifier_config,
    reddit,
):
    """Test that the username is retrieved from `PRAW` correctly."""
    reddit_cutifier = RedditCutifier(reddit_cutifier_config)
    reddit_cutifier.reddit = reddit

    assert reddit_cutifier.username == "cute_tester"

    reddit.user.me.return_value = None

    with pytest.raises(AttributeError):
        assert reddit_cutifier.username


@patch.object(OAuthHelper, "authorize")
@patch("praw.Reddit")
def test_submit_post(
    mock_reddit,
    mock_oauth_helper_authorize,
    reddit_cutifier_config,
    reddit,
    post,
):
    """
    Test that :meth:`RedditCutifier.submit_post()` uses `PRAW` correctly.

    1. Test a successful post submission.

    2. Test an error handling during the submission.
    """
    reddit_cutifier = RedditCutifier(reddit_cutifier_config)
    reddit_cutifier.reddit = reddit

    permalink = reddit_cutifier.submit_post(post)

    assert permalink == "slow_start_post_link"
    assert reddit.subreddit.return_value.submit.call_count == 1

    reddit.subreddit.return_value.submit.side_effect = PrawcoreException

    with pytest.raises(RedditError):
        reddit_cutifier.submit_post(post)


@pytest.fixture()
def reddit_cutifier_config():
    """Return the mock `Config` for testing the `RedditCutifier`."""
    return MockConfig({
        "reddit": {
            "client_id": "fluffy_client_id",
            "client_secret": None,
            "user_agent": "Slow Start Rewatch Client",
        },
        "http_server": {
            "hostname": HTTP_SERVER_HOSTNAME,
            "port": HTTP_SERVER_PORT,
        },
    })
