# -*- coding: utf-8 -*-

from datetime import datetime
from unittest.mock import patch

import pytest

from slow_start_rewatch.exceptions import ImageNotFound, PostConversionError
from slow_start_rewatch.post import Post
from slow_start_rewatch.post_helper import PostHelper
from slow_start_rewatch.reddit.text_post_converter import TextPostConverter
from slow_start_rewatch.schedule.schedule import Schedule
from tests.conftest import MockConfig


@patch.object(PostHelper, "prepare_thumbnail")
def test_prepare_post(
    mock_prepare_thumbnail,
    post_helper_config,
    reddit,
):
    """
    Test the preparation of the post body.

    1. Prepare post without thumbnail.

    2. Prepare post with thumbnail.
    """
    posts = [
        Post(
            name="e{0:02}".format(post),
            submit_at=datetime(2018, 1, 6, 17, 0, 0),
            subreddit="anime",
            title="Slow Start - Episode {0} Discussion".format(post),
            body_template="1:$e01|2:$e02|3:$e03",
            navigation_scheduled="-",
            navigation_submitted="$link",
            navigation_current="*",
        ) for post in range(1, 4)
    ]
    posts[0].submission_id = "cute_id"
    schedule = Schedule(subreddit="anime", posts=posts)

    post_helper = PostHelper(post_helper_config, reddit)

    post_helper.prepare_post(posts[1], schedule)

    assert posts[1].body_md == "1:/cute_id|2:*|3:-"
    assert posts[0].body_md is None
    assert mock_prepare_thumbnail.call_count == 0

    post_helper.prepare_post(posts[0], schedule, prepare_thumbnail=True)
    assert posts[0].body_md == "1:*|2:-|3:-"
    assert mock_prepare_thumbnail.call_count == 1


@patch.object(TextPostConverter, "convert_to_rtjson")
def test_prepare_thumbnail(
    mock_convert_to_rtjson,
    post_helper_config,
    reddit,
    post,
):
    """
    Test the preparation of the post thumbnail.

    1. The post is converted successfully.

    2. The image is not found and :attr:`Post.submit_with_thumbnail` should be
       set to `False`.

    3. The conversion fails (an exception is raised).
    """
    mock_convert_to_rtjson.side_effect = [
        [{"content": "Slow Start"}],
        ImageNotFound("Image not found."),
        PostConversionError("Post conversion failed"),
    ]

    post_helper = PostHelper(post_helper_config, reddit)

    post_helper.prepare_thumbnail(post)

    assert post.body_rtjson[0]["content"] == "Slow Start"

    assert post.submit_with_thumbnail

    post_helper.prepare_thumbnail(post)

    assert not post.submit_with_thumbnail

    with pytest.raises(PostConversionError):
        post_helper.prepare_thumbnail(post)


@pytest.fixture()
def post_helper_config():
    """Return mock Config for testing the `PostHelper`."""
    return MockConfig({
        "reddit": {"user_agent": "Slow Start Rewatch Client"},
        "post_image_mime_types": "",
    })
