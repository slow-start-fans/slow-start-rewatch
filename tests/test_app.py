# -*- coding: utf-8 -*-

from unittest.mock import patch

import pytest

from slow_start_rewatch.app import App
from tests.conftest import MockConfig


@patch("slow_start_rewatch.app.Scheduler")
@patch("slow_start_rewatch.app.Timer")
@patch("slow_start_rewatch.app.RedditCutifier")
def test_run_successfully(
    reddit_cutifier,
    timer,
    scheduler,
    post,
    capsys,
):
    """Test that the App instantiates and uses other components."""
    reddit_cutifier.return_value.username = "cute_tester"
    scheduler.return_value.scheduled_post = post

    app = App(MockConfig())
    app.run()
    captured = capsys.readouterr()

    assert reddit_cutifier.return_value.authorize.call_count == 1
    assert scheduler.return_value.load.call_count == 1
    assert timer.return_value.wait.call_count == 1

    assert "Logged in as: cute_tester" in captured.out
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
