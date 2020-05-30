# -*- coding: utf-8 -*-

from unittest.mock import patch

import pytest

from slow_start_rewatch.app import App
from tests.conftest import MockConfig


@patch("slow_start_rewatch.app.Scheduler")
@patch("slow_start_rewatch.app.Timer")
def test_run_successfully(
    timer,
    scheduler,
    post,
    capsys,
):
    """Test that the App instantiates and uses other components."""
    scheduler.return_value.scheduled_post = post

    app = App(MockConfig({"username": "cute_tester"}))
    app.run()
    captured = capsys.readouterr()

    assert scheduler.return_value.load.call_count == 1
    assert timer.return_value.wait.call_count == 1

    assert "Slow Start" in captured.out


@patch("slow_start_rewatch.app.Scheduler")
@patch("slow_start_rewatch.app.Timer")
def test_start_invalid_call(timer, scheduler):
    """Test that :meth:`App.start()` cannot be called early."""
    scheduler.return_value.scheduled_post = None
    app = App(MockConfig({"username": "cute_tester"}))

    with pytest.raises(RuntimeError):
        app.start()

    assert timer.return_value.wait.call_count == 0
