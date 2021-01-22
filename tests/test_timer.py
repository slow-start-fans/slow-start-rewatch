# -*- coding: utf-8 -*-

from datetime import datetime
from unittest.mock import call, patch

import pytest

from slow_start_rewatch.exceptions import Abort
from slow_start_rewatch.timer import Timer
from tests.conftest import MockConfig


@patch("slow_start_rewatch.timer.time")
@patch("slow_start_rewatch.timer.datetime")
def test_countdown(mock_datetime, mock_time, timer_config):
    """
    Test that countdown works correctly.

    The time is mocked in such a way that it returns a value that occurs
    shortly after each tick with one exception which is meant to simulate
    a delay in the execution. When the delay occurs the :meth:`sleep()` calls
    should be skipped.
    """
    timer = Timer(timer_config)

    mock_datetime.utcnow.side_effect = [
        datetime(2018, 1, 6, 16, 59, 59),
        datetime(2018, 1, 6, 16, 59, 59, 10 * 1000),
        datetime(2018, 1, 6, 16, 59, 59, 210 * 1000),
        # Simulating delay in execution
        datetime(2018, 1, 6, 16, 59, 59, 805 * 1000),
        datetime(2018, 1, 6, 16, 59, 59, 810 * 1000),
        datetime(2018, 1, 6, 17, 0, 0, 100 * 1000),
    ]

    timer.wait(datetime(2018, 1, 6, 17, 0, 0))

    # List multiply forbidden by WPS435
    expected_calls = [call(0.19) for index in range(2)]

    assert list(mock_time.sleep.call_args_list) == expected_calls


@patch("slow_start_rewatch.timer.datetime")
def test_start_after_target_time(mock_datetime, timer_config):
    """Test starting the timer after the target time."""
    timer = Timer(timer_config)

    mock_datetime.utcnow.return_value = datetime(2018, 1, 6, 18, 0, 0)

    with pytest.raises(RuntimeError):
        timer.wait(datetime(2018, 1, 6, 17, 0, 0))


@patch("slow_start_rewatch.timer.Timer.countdown")
@patch("slow_start_rewatch.timer.datetime")
def test_abort(mock_datetime, mock_countdown, timer_config):
    """Test aborting the countdown."""
    timer = Timer(timer_config)

    mock_countdown.side_effect = KeyboardInterrupt
    mock_datetime.utcnow.return_value = datetime(2018, 1, 6, 16, 59, 59)

    with pytest.raises(Abort):
        timer.wait(datetime(2018, 1, 6, 17, 0, 0))


def test_ticks(timer_config):
    """
    Test that the ticks are generated properly.

    The Start Time is shifted in between the ticks to test that the ticks are
    generated from the end (synced with the Target Time).
    """
    timer = Timer(timer_config)

    with pytest.raises(AttributeError):
        timer.ticks()

    timer.start_time = datetime(2018, 1, 6, 16, 59, 59, 100 * 1000)
    timer.target_time = datetime(2018, 1, 6, 17, 0, 0)

    expected_timestamps = [
        datetime(2018, 1, 6, 16, 59, 59, 200 * 1000),
        datetime(2018, 1, 6, 16, 59, 59, 400 * 1000),
        datetime(2018, 1, 6, 16, 59, 59, 600 * 1000),
        datetime(2018, 1, 6, 16, 59, 59, 800 * 1000),
        datetime(2018, 1, 6, 17, 0, 0),
    ]

    expected_ticks = [
        int(tick_datetime.timestamp() * 1000)
        for tick_datetime in expected_timestamps
    ]

    generated_ticks = list(timer.ticks())

    assert generated_ticks == expected_ticks


@pytest.mark.parametrize(("tick_datetime", "expected_time_left"), [
    (datetime(2018, 1, 6, 15, 59, 59, 100 * 1000), "1:00:01"),
    (datetime(2018, 1, 6, 16, 59, 59, 900 * 1000), "0:00:01"),
    (datetime(2018, 1, 6, 17), "0:00:00"),
    (None, ""),
],
)
def test_time_left(tick_datetime, expected_time_left, timer_config):
    """Test that the remaining time is rendered correctly."""
    timer = Timer(
        config=timer_config,
        target_time=datetime(2018, 1, 6, 17, 0, 0),
    )

    tick = int(tick_datetime.timestamp() * 1000) if tick_datetime else None

    time_left = timer.time_left(tick)

    assert time_left == expected_time_left


def test_time_left_invalid_call(timer_config):
    """Test calling :meth:`Timer.time_left()` without required attributes."""
    timer = Timer(timer_config)

    with pytest.raises(AttributeError):
        timer.time_left(1000)


@pytest.fixture()
def timer_config():
    """Return mock Config for testing the `Timer`."""
    return MockConfig({"timer": {"refresh_interval": 200}})
