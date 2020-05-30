# -*- coding: utf-8 -*-

from datetime import datetime
from unittest.mock import call, patch

import pytest

from slow_start_rewatch.exceptions import Abort, EmptySchedule
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

    mock_datetime.now.side_effect = [
        datetime(2018, 1, 6, 11, 59, 59),
        datetime(2018, 1, 6, 11, 59, 59, 10 * 1000),
        datetime(2018, 1, 6, 11, 59, 59, 210 * 1000),
        # Simulating delay in execution
        datetime(2018, 1, 6, 11, 59, 59, 805 * 1000),
        datetime(2018, 1, 6, 11, 59, 59, 810 * 1000),
        datetime(2018, 1, 6, 12, 0, 0, 100 * 1000),
    ]

    timer.wait(datetime(2018, 1, 6, 12, 0, 0))

    # List multiply forbidden by WPS435
    expected_calls = [call(0.19) for index in range(2)]

    assert list(mock_time.sleep.call_args_list) == expected_calls


@patch("slow_start_rewatch.timer.datetime")
def test_empty_schedule(mock_datetime, timer_config):
    """Test starting the timer after the scheduled time."""
    timer = Timer(timer_config)

    mock_datetime.now.return_value = datetime(2018, 1, 6, 13, 0, 0)

    with pytest.raises(EmptySchedule):
        timer.wait(datetime(2018, 1, 6, 12, 0, 0))


@patch("slow_start_rewatch.timer.Timer.countdown")
@patch("slow_start_rewatch.timer.datetime")
def test_abort(mock_datetime, mock_countdown, timer_config):
    """Test aborting the countdown."""
    timer = Timer(timer_config)

    mock_countdown.side_effect = KeyboardInterrupt
    mock_datetime.now.return_value = datetime(2018, 1, 6, 11, 59, 59)

    with pytest.raises(Abort):
        timer.wait(datetime(2018, 1, 6, 12, 0, 0))


def test_ticks(timer_config):
    """
    Test that the ticks are generated properly.

    The Start Time is shifted in between the ticks to test that the ticks are
    generated from the end (synced with the Target Time).
    """
    timer = Timer(timer_config)

    with pytest.raises(AttributeError):
        timer.ticks()

    timer.start_time = datetime(2018, 1, 6, 11, 59, 59, 100 * 1000)
    timer.target_time = datetime(2018, 1, 6, 12, 0, 0)

    expected_timestamps = [
        datetime(2018, 1, 6, 11, 59, 59, 200 * 1000),
        datetime(2018, 1, 6, 11, 59, 59, 400 * 1000),
        datetime(2018, 1, 6, 11, 59, 59, 600 * 1000),
        datetime(2018, 1, 6, 11, 59, 59, 800 * 1000),
        datetime(2018, 1, 6, 12, 0, 0),
    ]

    expected_ticks = [
        int(tick_datetime.timestamp() * 1000)
        for tick_datetime in expected_timestamps
    ]

    generated_ticks = list(timer.ticks())

    assert generated_ticks == expected_ticks


@pytest.fixture()
def timer_config():
    """Return mock Config for testing Timer."""
    return MockConfig({"timer": {"refresh_interval": 200}})
