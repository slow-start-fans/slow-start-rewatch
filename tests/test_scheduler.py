# -*- coding: utf-8 -*-

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from slow_start_rewatch.exceptions import MissingSchedule
from slow_start_rewatch.post import Post
from slow_start_rewatch.schedule.schedule import Schedule
from slow_start_rewatch.schedule.scheduler import Scheduler
from tests.conftest import MockConfig


@patch("slow_start_rewatch.schedule.scheduler.ScheduleFileStorage")
@patch("slow_start_rewatch.schedule.scheduler.PostHelper")
def test_load(
    mock_post_helper,
    mock_schedule_file_storage,
    scheduler_config,
    reddit,
):
    """Test loading of the Schedule."""
    mock_schedule_file_storage.return_value.load.return_value = Mock(
        subreddit="FileSource",
    )

    scheduler = Scheduler(scheduler_config, reddit)

    scheduler.load()
    assert scheduler.schedule
    assert scheduler.schedule.subreddit == "FileSource"

    # Clear the file name
    scheduler_config["schedule_file"] = None
    with pytest.raises(MissingSchedule):
        Scheduler(scheduler_config, reddit)


@patch("slow_start_rewatch.schedule.scheduler.datetime")
def test_get_scheduled_posts(mock_datetime, scheduler, schedule):
    """Test the generator of the scheduled posts."""
    mock_datetime.utcnow.side_effect = [
        datetime(2018, 1, 6 + 7, 16, 50, 0),
        datetime(2018, 1, 6 + 14, 16, 50, 0),
        datetime(2018, 1, 6 + 21, 16, 50, 0),
    ]

    scheduler.schedule = schedule

    post = next(scheduler.get_scheduled_posts())
    assert post.submit_at == datetime(2018, 1, 6 + 7, 17, 0, 0)

    post = next(scheduler.get_scheduled_posts())
    assert post.submit_at == datetime(2018, 1, 6 + 14, 17, 0, 0)

    with pytest.raises(StopIteration):
        next(scheduler.get_scheduled_posts())


@patch("slow_start_rewatch.schedule.scheduler.datetime")
def test_get_next_post_not_submitted(mock_datetime, scheduler, schedule):
    """
    Test that submitted posts are not included in scheduled posts.

    The first post is configured as submitted and it is expected to be skipped.
    """
    mock_datetime.utcnow.return_value = datetime(2018, 1, 6, 16, 50, 0)

    schedule.posts[0].submission_id = "cute_id"
    scheduler.schedule = schedule

    post = scheduler.get_next_post()
    assert post
    assert post.submit_at == datetime(2018, 1, 6 + 7, 17, 0, 0)


def test_get_submitted_posts(scheduler, schedule):
    """Test getting submitted posts."""
    scheduler.schedule = schedule

    schedule.posts[0].submission_id = "cute_id_1"
    schedule.posts[1].submission_id = "cute_id_2"

    assert len(scheduler.get_submitted_posts()) == 2

    posts = scheduler.get_submitted_posts(skip_post=schedule.posts[0])

    assert posts[0] == schedule.posts[1]


def test_save_schedule(scheduler, schedule):
    """Test saving the schedule."""
    scheduler.schedule = schedule

    scheduler.save_schedule()

    assert scheduler.schedule_storage.save.called


def test_scheduler_errors(scheduler: Scheduler):
    """Test scheduler errors when the schedule is not loaded."""
    with pytest.raises(RuntimeError):
        scheduler.get_next_post()

    with pytest.raises(RuntimeError):
        scheduler.get_submitted_posts()

    with pytest.raises(RuntimeError):
        scheduler.save_schedule()


@pytest.fixture()
@patch("slow_start_rewatch.schedule.scheduler.PostHelper")
@patch("slow_start_rewatch.schedule.scheduler.ScheduleFileStorage")
def scheduler(
    mock_post_helper,
    mock_schedule_file_storage,
    scheduler_config,
    reddit,
):
    """Return the `Scheduler` configured for testing."""
    return Scheduler(scheduler_config, reddit)


@pytest.fixture()
def schedule():
    """Return the `Schedule` with 3 posts."""
    posts = [
        Post(
            name="episode_{0}".format(index + 1),
            submit_at=datetime(2018, 1, 6 + index * 7, 17, 0, 0),
            subreddit="anime",
            title="Slow Start - Episode {0} Discussion".format(index + 1),
            body_template="*Slow Start*, Episode {0}".format(index + 1),
        ) for index in range(0, 3)
    ]
    return Schedule(subreddit="anime", posts=posts)


@pytest.fixture()
def scheduler_config():
    """Return mock Config with the file storage configured."""
    return MockConfig({
        "schedule_file": "schedule.yml",
    })
