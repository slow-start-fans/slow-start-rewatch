# -*- coding: utf-8 -*-

from datetime import datetime
from unittest.mock import call, patch

import pytest

from slow_start_rewatch.exceptions import ImageNotFound, PostConversionError
from slow_start_rewatch.post import Post
from slow_start_rewatch.post_helper import PostHelper
from slow_start_rewatch.reddit.text_post_converter import TextPostConverter
from slow_start_rewatch.schedule.schedule import Schedule
from tests.conftest import MockConfig


@patch.object(PostHelper, "build_navigation_links")
@patch.object(PostHelper, "prepare_thumbnail")
def test_prepare_post(
    mock_prepare_thumbnail,
    mock_build_navigation_links,
    post_helper_config,
    reddit,
):
    """
    Test the preparation of the post body.

    1. Prepare post without thumbnail.

    2. Prepare post with thumbnail.
    """
    mock_build_navigation_links.return_value = "links"
    posts = [
        Post(
            name="e{0:02}".format(post),
            submit_at=datetime(2018, 1, 6, 17, 0, 0),
            subreddit="anime",
            title="Slow Start - Episode {0} Discussion".format(post),
            body_template="$navigation_links|1:$e01|2:$e02|3:$e03",
            navigation_scheduled="-",
            navigation_submitted="$link",
            navigation_current="*",
        ) for post in range(1, 4)
    ]
    posts[0].submission_id = "cute_id"
    schedule = Schedule(subreddit="anime", posts=posts)

    post_helper = PostHelper(post_helper_config, reddit)

    post_helper.prepare_post(posts[1], schedule)

    assert posts[1].body_md == "links|1:/cute_id|2:*|3:-"
    assert posts[0].body_md is None
    assert mock_prepare_thumbnail.call_count == 0

    post_helper.prepare_post(posts[0], schedule, prepare_thumbnail=True)
    assert posts[0].body_md == "links|1:*|2:-|3:-"
    assert mock_prepare_thumbnail.call_count == 1


@patch.object(PostHelper, "substitute_navigation_links")
def test_build_navigation_links(
    mock_substitute_navigation_links,
    post_helper_config,
    reddit,
):
    """Test the preparation of the Navigation Links."""
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
    post_helper = PostHelper(post_helper_config, reddit)

    post_helper.build_navigation_links(posts[0], posts)
    assert mock_substitute_navigation_links.call_args == call(None, None)

    posts[0].submission_id = "id_1"
    post_helper.build_navigation_links(posts[1], posts)
    assert mock_substitute_navigation_links.call_args == call("id_1", None)

    posts[1].submission_id = "id_2"
    post_helper.build_navigation_links(posts[0], posts)
    assert mock_substitute_navigation_links.call_args == call(None, "id_2")

    posts[2].submission_id = "id_3"
    post_helper.build_navigation_links(posts[1], posts)
    assert mock_substitute_navigation_links.call_args == call("id_1", "id_3")


@pytest.mark.parametrize(("previous_id", "next_id", "expected_output"), [
    ("cute_id_1", "cute_id_2", "/cute_id_1/cute_id_2"),
    ("cute_id_1", None, "/cute_id_1"),
    (None, "cute_id_2", "/cute_id_2"),
    (None, None, ""),
],
)
def test_substitute_navigation_links(
    previous_id,
    next_id,
    expected_output,
    post_helper_config,
    reddit,
):
    """Test the substitution of the Navigation Links."""
    post_helper = PostHelper(post_helper_config, reddit)

    output = post_helper.substitute_navigation_links(previous_id, next_id)

    assert output == expected_output


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
        "navigation_links": {
            "placeholder": "navigation_links",
            "template_empty": "",
            "template_previous": "$previous_link",
            "template_next": "$next_link",
            "template_both": "$previous_link$next_link",
        },
        "post_image_mime_types": "",
    })
