# -*- coding: utf-8 -*-

import io
from unittest.mock import DEFAULT, call, patch

import pytest
from praw.exceptions import PRAWException
from requests.exceptions import HTTPError

from slow_start_rewatch.exceptions import RedditError
from slow_start_rewatch.reddit.reddit_helper import (
    API_PATH_CONVERT,
    RedditHelper,
)
from tests.conftest import MockConfig


def test_convert_to_rtjson(
    reddit_helper_config,
    reddit,
):
    """Test converting Markdown to Reddit Rich Text JSON."""
    reddit_helper = RedditHelper(reddit_helper_config, reddit)

    rtjson_sample = [{"c": [{"e": "text", "t": "Cute Content"}], "e": "par"}]
    reddit.post.side_effect = [
        PRAWException,
        {
            "data": "missing",
        },
        {
            "output_mode": "markdown",
            "output": "Cute Content",
        },
        {
            "output_mode": "rtjson",
            "output": {
                "document": rtjson_sample,
            },
        },
    ]

    with pytest.raises(RedditError) as reddit_error:
        reddit_helper.convert_to_rtjson("Cute Content")

    # Comply with PT012: https://pypi.org/project/flake8-pytest-style/
    assert "Error when converting" in str(reddit_error.value)  # noqa: WPS441

    with pytest.raises(RedditError) as missing_error:
        reddit_helper.convert_to_rtjson("Cute Content")

    assert "Missing output" in str(missing_error.value)  # noqa: WPS441

    with pytest.raises(RedditError) as invalid_error:
        reddit_helper.convert_to_rtjson("Cute Content")

    assert "Invalid output" in str(invalid_error.value)  # noqa: WPS441

    assert reddit_helper.convert_to_rtjson("Cute Content") == rtjson_sample
    assert reddit.post.call_args == call(
        API_PATH_CONVERT,
        data={
            "output_mode": "rtjson",
            "markdown_text": "Cute Content",
        },
    )


@patch("requests.post")
def test_upload_image(
    mock_post,
    reddit_helper_config,
    reddit,
):
    """Test uploading an image to the Reddit hosting."""
    reddit_helper = RedditHelper(reddit_helper_config, reddit)

    reddit.post.return_value = {
        "args": {
            "fields": [
                {"name": "Hana", "value": "4/6"},
                {"name": "Tama", "value": "5/23"},
                {"name": "Eiko", "value": "6/20"},
                {"name": "Kamuri", "value": "10/30"},
            ],
            "action": "//slow-start.com/",
        },
        "asset": {
            "asset_id": "adorable_id",
        },
    }
    reddit.post.side_effect = [
        PRAWException,
        DEFAULT,
        DEFAULT,
    ]
    mock_post.return_value.raise_for_status.side_effect = [
        HTTPError,
        None,
    ]

    image_bytes = io.BytesIO(b"GIF89a")

    with pytest.raises(RedditError) as lease_error:
        reddit_helper.upload_image("flowery_hug.gif", "image/gif", image_bytes)

    # Comply with PT012: https://pypi.org/project/flake8-pytest-style/
    assert "Error when preparing" in str(lease_error.value)  # noqa: WPS441

    with pytest.raises(RedditError) as upload_error:
        reddit_helper.upload_image("flowery_hug.gif", "image/gif", image_bytes)

    assert "Error when uploading" in str(upload_error.value)  # noqa: WPS441

    asset_id = reddit_helper.upload_image(
        "flowery_hug.gif",
        "image/gif",
        image_bytes,
    )

    assert asset_id == "adorable_id"
    assert mock_post.call_args == call(
        "https://slow-start.com/",
        data={
            "Hana": "4/6",
            "Tama": "5/23",
            "Eiko": "6/20",
            "Kamuri": "10/30",
        },
        files={"file": ("flowery_hug.gif", image_bytes)},
        headers={"User-Agent": "Slow Start Rewatch Client"},
    )


def test_submit_post_rtjson(
    reddit_helper_config,
    reddit,
):
    """Test submitting a post with the Reddit Rich Text JSON body."""
    reddit_helper = RedditHelper(reddit_helper_config, reddit)

    reddit_helper.submit_post_rtjson(
        subreddit="anime",
        title="Slow Start Rewatch - Episode 1 Discussion",
        body_rtjson=[{"c": [{"t": "Awesome Content"}]}],
    )

    assert reddit.post.called


@pytest.fixture()
def reddit_helper_config():
    """Return mock Config for testing the `RedditHelper`."""
    return MockConfig({"reddit": {"user_agent": "Slow Start Rewatch Client"}})
