# -*- coding: utf-8 -*-

from typing import Optional
from unittest.mock import call, patch

import pytest
from prawcore.exceptions import PrawcoreException

from slow_start_rewatch.exceptions import RedditError
from slow_start_rewatch.post import Post
from slow_start_rewatch.reddit.reddit_cutifier import RedditCutifier
from tests.conftest import (
    HTTP_SERVER_HOSTNAME,
    HTTP_SERVER_PORT,
    REFRESH_TOKEN,
    MockConfig,
)

REDDIT_USER_AGENT = "Slow Start Rewatch Client"
REDDIT_CLIENT_ID = "fluffy_client_id"
REDDIT_CLIENT_SECRET: Optional[str] = None


@patch("slow_start_rewatch.reddit.reddit_cutifier.OAuthHelper")
@patch("slow_start_rewatch.reddit.reddit_cutifier.Reddit")
def test_authorize(
    mock_reddit,
    mock_oauth_helper,
    reddit_cutifier_config,
):
    """
    Test the Reddit authorization.

    1. Ensure that the `Reddit` instance is initialized with the correct
       arguments.

    2. Check that the :meth:`OAuthHelper.authorize()` is called during the
       authorization.
    """
    reddit_cutifier = RedditCutifier(reddit_cutifier_config)

    redirect_uri = "http://{0}:{1}/".format(
        HTTP_SERVER_HOSTNAME,
        HTTP_SERVER_PORT,
    )

    assert mock_reddit.call_args == call(
        user_agent=REDDIT_USER_AGENT,
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        redirect_uri=redirect_uri,
        refresh_token=REFRESH_TOKEN,
    )

    reddit_cutifier.authorize()

    assert mock_oauth_helper.return_value.authorize.called


@patch("slow_start_rewatch.reddit.reddit_cutifier.Reddit")
def test_username(
    mock_reddit,
    reddit_cutifier_config,
):
    """Test that the username is retrieved from `PRAW` correctly."""
    reddit_cutifier = RedditCutifier(reddit_cutifier_config)
    reddit_user_me = mock_reddit.return_value.user.me

    reddit_user_me.return_value.name = "cute_tester"

    assert reddit_cutifier.username == "cute_tester"

    reddit_user_me.return_value = None

    with pytest.raises(AttributeError):
        assert reddit_cutifier.username


@patch("slow_start_rewatch.reddit.reddit_cutifier.Reddit")
def test_submit_post_without_thumbnail(
    mock_reddit,
    reddit_cutifier_config,
    post: Post,
):
    """
    Test submitting a post.

    1. Test successful submission:

    Check that :meth:`Reddit.subreddit().submit()` is called with the correct
    arguments.

    2. Test handling of an exception raised by `PRAW`.
    """
    reddit_cutifier = RedditCutifier(reddit_cutifier_config)

    subreddit = mock_reddit.return_value.subreddit.return_value
    subreddit.submit.return_value.permalink = "slow_start_post_link"

    assert reddit_cutifier.submit_post(post) == "slow_start_post_link"
    assert subreddit.submit.call_args == call(
        title=post.title,
        selftext=post.body_md,
    )

    subreddit.submit.side_effect = PrawcoreException
    with pytest.raises(RedditError):
        reddit_cutifier.submit_post(post)


@pytest.fixture()
def reddit_cutifier_config():
    """Return the mock `Config` for testing the `RedditCutifier`."""
    config = MockConfig({
        "reddit": {
            "user_agent": REDDIT_USER_AGENT,
            "client_id": REDDIT_CLIENT_ID,
            "client_secret": REDDIT_CLIENT_SECRET,
        },
        "http_server": {
            "hostname": HTTP_SERVER_HOSTNAME,
            "port": HTTP_SERVER_PORT,
        },
    })

    config.refresh_token = REFRESH_TOKEN

    return config
