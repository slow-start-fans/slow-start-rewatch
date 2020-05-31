# -*- coding: utf-8 -*-

from unittest.mock import patch

import pytest

from slow_start_rewatch.app import App
from tests.conftest import MockConfig


@patch("slow_start_rewatch.app.App.start")
@patch("slow_start_rewatch.app.App.prepare")
@patch("slow_start_rewatch.app.Scheduler")
@patch("slow_start_rewatch.app.Timer")
@patch("slow_start_rewatch.app.RedditCutifier")
def test_run(
    mock_reddit_cutifier,
    mock_timer,
    mock_scheduler,
    mock_prepare,
    mock_start,
):
    """Test that the App instantiates the other components."""
    app = App(MockConfig())
    app.run()

    assert mock_reddit_cutifier.call_count == 1
    assert mock_timer.call_count == 1
    assert mock_scheduler.call_count == 1

    assert mock_prepare.call_count == 1
    assert mock_start.call_count == 1


@patch("slow_start_rewatch.app.Scheduler")
@patch("slow_start_rewatch.app.Timer")
@patch("slow_start_rewatch.app.RedditCutifier")
def test_prepare(
    mock_reddit_cutifier,
    mock_timer,
    mock_scheduler,
    capsys,
):
    """Test that the :meth:`App.prepare()` runs properly."""
    mock_reddit_cutifier.return_value.username = "cute_tester"

    app = App(MockConfig())
    app.prepare()
    captured = capsys.readouterr()

    assert mock_reddit_cutifier.return_value.authorize.call_count == 1
    assert mock_scheduler.return_value.load.call_count == 1

    assert "Logged in as: cute_tester" in captured.out


@patch("slow_start_rewatch.app.Scheduler")
@patch("slow_start_rewatch.app.Timer")
@patch("slow_start_rewatch.app.RedditCutifier")
def test_start(
    reddit_cutifier,
    timer,
    scheduler,
    post,
    capsys,
):
    """Test that the :meth:`App.start()` runs properly."""
    scheduler.return_value.scheduled_post = post

    app = App(MockConfig())
    app.start()
    captured = capsys.readouterr()

    assert timer.return_value.wait.call_count == 1
    assert reddit_cutifier.return_value.submit_post.call_count == 1

    assert "Slow Start" in captured.out


@patch("slow_start_rewatch.app.Scheduler")
@patch("slow_start_rewatch.app.Timer")
@patch("slow_start_rewatch.app.RedditCutifier")
def test_start_invalid_call(reddit_cutifier, timer, scheduler):
    """Test that :meth:`App.start()` cannot be called early."""
    scheduler.return_value.scheduled_post = None
    app = App(MockConfig())

    with pytest.raises(RuntimeError):
        app.start()

    assert timer.return_value.wait.call_count == 0
