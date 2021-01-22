# -*- coding: utf-8 -*-

from datetime import datetime

import pytest

from slow_start_rewatch.post import Post


def test_create():
    """Test creating a `Post` instance."""
    post = Post(
        name="episode_01",
        submit_at=datetime(2018, 1, 6, 17, 0, 0),
        subreddit="anime",
        title="Slow Start - Episode 1 Discussion",
        body_template="*Slow Start*, Episode 1",
    )

    assert post.submit_at == datetime(2018, 1, 6, 17, 0, 0)
    assert post.subreddit == "anime"
    assert post.title == "Slow Start - Episode 1 Discussion"
    assert post.body_template == "*Slow Start*, Episode 1"

    assert (
        post.submit_with_thumbnail,
        post.flair_id,
        post.navigation_submitted,
        post.navigation_current,
        post.navigation_scheduled,
        post.submission_id,
        post.body_md,
        post.body_rtjson,
    ) == (
        True,  # Set to True by default
        None,
        "$link",  # Default value
        "",  # Default value
        "",  # Default value
        None,
        None,
        None,
    )


def test_create_with_empty_field():
    """Test that the `Post` cannot be instantiated with empty attributes."""
    with pytest.raises(AttributeError):
        Post(
            name="episode_01",
            submit_at=datetime(2018, 1, 6, 17, 0, 0),
            subreddit="anime",
            title="Slow Start - Episode 1 Discussion",
            body_template=None,  # type: ignore
        )


def test_comparison():
    """Test the comparison of `Post` objects."""
    post = Post(
        name="episode_01",
        submit_at=datetime(2018, 1, 6, 17, 0, 0),
        subreddit="anime",
        title="Slow Start - Episode 1 Discussion",
        body_template="*Slow Start*, Episode 1: The First Butterflies",
    )

    identical_post = Post(
        name="episode_01",
        submit_at=datetime(2018, 1, 6, 17, 0, 0),
        subreddit="anime",
        title="Slow Start - Episode 1 Discussion",
        body_template="*Slow Start*, Episode 1: The First Butterflies",
    )

    different_post = Post(
        name="episode_02",
        submit_at=datetime(2018, 1, 13, 12, 0, 0),
        subreddit="anime",
        title="Slow Start - Episode 2 Discussion",
        body_template="*Slow Start*, Episode 2: Exercise Wears Me Out ",
    )

    assert post == identical_post
    assert post != different_post
    assert post.__eq__("post") is NotImplemented  # noqa: WPS609


def test_string_representation():
    """Test the string representation of a `Post` instance."""
    post = Post(
        name="episode_01",
        submit_at=datetime(2018, 1, 6, 17, 0, 0),
        subreddit="anime",
        title="Slow Start - Episode 1 Discussion",
        body_template="*Slow Start*, Episode 1: The First Butterflies",
    )

    assert "/r/anime Post at 2018-01-06 17:00:00: Slow Start" in str(post)
