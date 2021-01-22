# -*- coding: utf-8 -*-

from datetime import datetime

import pytest

from slow_start_rewatch.post import Post
from slow_start_rewatch.schedule.schedule import Schedule


def test_create():
    """Test creating a `Post` instance."""
    posts = [
        Post(
            name="episode_{0}".format(post_id),
            submit_at=datetime(2018, 1, 6, 17, 0, 0),
            subreddit="anime",
            title="Slow Start - Episode {0} Discussion".format(post_id),
            body_template="*Slow Start*, Episode {0}".format(post_id),
        ) for post_id in range(1, 4)
    ]
    schedule = Schedule(subreddit="anime", posts=posts)

    assert schedule.subreddit == "anime"
    assert schedule.posts[0].subreddit == "anime"
    assert schedule.posts[1].title == "Slow Start - Episode 2 Discussion"
    assert schedule.posts[2].submit_with_thumbnail  # Set to True by default


def test_create_with_empty_field():
    """Test that the `Schedule` requires `subreddit` field when created."""
    with pytest.raises(AttributeError):
        Schedule(
            subreddit=None,  # type: ignore
        )


@pytest.mark.parametrize(("other_subreddit", "other_post_ids", "identical"), [
    pytest.param(
        "anime",
        [1, 2],
        1,
        id="identical",
    ),
    pytest.param(
        "awwnime",
        [1, 2],
        0,
        id="different_subreddit",
    ),
    pytest.param(
        "anime",
        [1],
        0,
        id="different_post_count",
    ),
    pytest.param(
        "anime",
        [1, 3],
        0,
        id="different_posts",
    ),
])
def test_comparison(other_subreddit, other_post_ids, identical):
    """Test the comparison of `Post` objects."""
    posts = [
        Post(
            name="episode_{0}".format(post_id),
            submit_at=datetime(2018, 1, 6, 17, 0, 0),
            subreddit="anime",
            title="Slow Start - Episode {0} Discussion".format(post_id),
            body_template="*Slow Start*, Episode {0}".format(post_id),
        ) for post_id in range(1, 3)
    ]
    schedule = Schedule(subreddit="anime", posts=posts)

    other_posts = [
        Post(
            name="episode_{0}".format(post_id),
            submit_at=datetime(2018, 1, 6, 17, 0, 0),
            subreddit="anime",
            title="Slow Start - Episode {0} Discussion".format(post_id),
            body_template="*Slow Start*, Episode {0}".format(post_id),
        ) for post_id in other_post_ids
    ]
    other_schedule = Schedule(subreddit=other_subreddit, posts=other_posts)

    if identical:
        assert schedule == other_schedule
    else:
        assert schedule != other_schedule

    assert schedule.__eq__("schedule") is NotImplemented  # noqa: WPS609
