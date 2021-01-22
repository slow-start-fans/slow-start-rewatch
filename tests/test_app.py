# -*- coding: utf-8 -*-

from unittest.mock import patch

import pytest

from slow_start_rewatch.app import App
from tests.conftest import MockConfig


@patch("slow_start_rewatch.app.Scheduler")
@patch("slow_start_rewatch.app.Timer")
@patch("slow_start_rewatch.app.RedditCutifier")
@patch("slow_start_rewatch.app.Config", return_value=MockConfig())
def test_init(
    mock_config,
    mock_reddit_cutifier,
    mock_timer,
    mock_scheduler,
):
    """Test that App parameters are stored to the Congig."""
    config = mock_config.return_value

    App()
    assert "schedule_file" not in config

    App(schedule_file="schedule.yml")
    assert config["schedule_file"] == "schedule.yml"


@patch("slow_start_rewatch.app.App.start")
@patch("slow_start_rewatch.app.App.prepare")
def test_run(
    mock_prepare,
    mock_start,
    app,
):
    """Test that the :meth:`App.run()` calls the correct methods."""
    app.run()

    assert mock_prepare.call_count == 1
    assert mock_start.call_count == 1


@patch("slow_start_rewatch.app.Scheduler")
@patch("slow_start_rewatch.app.Timer")
@patch("slow_start_rewatch.app.RedditCutifier")
@patch("slow_start_rewatch.app.Config", return_value=MockConfig())
def test_prepare(
    mock_config,
    mock_reddit_cutifier,
    mock_timer,
    mock_scheduler,
    app,
    capsys,
):
    """Test that the :meth:`App.prepare()` runs properly."""
    mock_reddit_cutifier.return_value.username = "cute_tester"

    app = App()
    app.prepare()
    captured = capsys.readouterr()

    assert mock_reddit_cutifier.return_value.authorize.call_count == 1
    assert mock_scheduler.return_value.load.call_count == 1

    assert "Logged in as: cute_tester" in captured.out


@patch("slow_start_rewatch.app.Scheduler")
@patch("slow_start_rewatch.app.Timer")
@patch("slow_start_rewatch.app.RedditCutifier")
@patch("slow_start_rewatch.app.Config", return_value=MockConfig())
def test_start(
    mock_config,
    mock_reddit_cutifier,
    mock_timer,
    mock_scheduler,
    post,
    capsys,
):
    """Test that the :meth:`App.start()` runs properly."""
    mock_scheduler.return_value.get_scheduled_posts.return_value = [post]

    app = App()
    app.start()
    captured = capsys.readouterr()

    assert mock_timer.return_value.wait.call_count == 1
    assert mock_reddit_cutifier.return_value.submit_post.call_count == 1

    assert "Slow Start" in captured.out

    assert mock_scheduler.return_value.save_schedule.call_count == 1
    assert mock_reddit_cutifier.return_value.update_posts.call_count == 1


@pytest.fixture()
@patch("slow_start_rewatch.app.Scheduler")
@patch("slow_start_rewatch.app.Timer")
@patch("slow_start_rewatch.app.RedditCutifier")
@patch("slow_start_rewatch.app.Config", return_value=MockConfig())
def app(
    mock_config,
    mock_reddit_cutifier,
    mock_timer,
    mock_scheduler,
):
    """Return the `App` configured for testing."""
    return App()
