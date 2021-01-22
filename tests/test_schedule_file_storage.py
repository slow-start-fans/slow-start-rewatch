# -*- coding: utf-8 -*-

import os
from pathlib import Path

import pytest

from slow_start_rewatch.exceptions import MissingPost, MissingSchedule
from slow_start_rewatch.schedule.schedule_file_storage import (
    ScheduleFileStorage,
)
from tests.conftest import TEST_ROOT_DIR, MockConfig
from tests.test_schedule_storage import POST_BODY, SCHEDULE_DATA

TEST_SCHEDULE_PATH = Path(TEST_ROOT_DIR).joinpath("test_schedule")
SCHEDULE_FILENAME = "schedule.yml"
POST_BODY_FILENAME = "episode_01.md"


def test_load_schedule_data(schedule_file_storage_config):
    """Test loading of the Schedule data from a file."""
    schedule_file_storage = ScheduleFileStorage(schedule_file_storage_config)

    schedule_data = schedule_file_storage.load_schedule_data()

    assert schedule_data == SCHEDULE_DATA


def test_load_schedule_data_error(tmpdir):
    """Test loading of the Schedule data from a nonexistent file."""
    schedule_path = tmpdir.join(SCHEDULE_FILENAME)
    config = MockConfig({"schedule_file": str(schedule_path)})

    schedule_file_storage = ScheduleFileStorage(config)

    assert not os.path.exists(schedule_path)

    with pytest.raises(MissingSchedule):
        schedule_file_storage.load_schedule_data()


def test_load_post_body(schedule_file_storage_config):
    """Test loading of the Post body from a file."""
    schedule_file_storage = ScheduleFileStorage(schedule_file_storage_config)

    post_body = schedule_file_storage.load_post_body(POST_BODY_FILENAME)

    assert post_body == POST_BODY


def test_load_post_body_error(tmpdir):
    """Test loading of the Post body from a file."""
    schedule_path = tmpdir.join(SCHEDULE_FILENAME)
    post_body_path = tmpdir.join(POST_BODY_FILENAME)
    config = MockConfig({"schedule_file": str(schedule_path)})

    schedule_file_storage = ScheduleFileStorage(config)

    assert not os.path.exists(post_body_path)

    with pytest.raises(MissingPost) as missing_post_error:
        schedule_file_storage.load_post_body(POST_BODY_FILENAME)

    # Comply with PT012: https://pypi.org/project/flake8-pytest-style/
    assert str(post_body_path) in str(missing_post_error.value)  # noqa: WPS441


def test_save_schedule_data(tmpdir):
    """Test saving of the Schedule data to a file."""
    schedule_path = tmpdir.join(SCHEDULE_FILENAME)
    config = MockConfig({"schedule_file": str(schedule_path)})

    schedule_file_storage = ScheduleFileStorage(config)

    assert not os.path.exists(schedule_path)

    schedule_file_storage.save_schedule_data(SCHEDULE_DATA)

    with open(schedule_path, encoding="utf-8") as schedule_file:
        schedule_data = schedule_file.read()

    assert schedule_data == SCHEDULE_DATA


def test_invalid_config():
    """Test initializing `ScheduleFileStorage` with invalid config."""
    config = MockConfig({"schedule_file": None})

    with pytest.raises(RuntimeError):
        ScheduleFileStorage(config)


@pytest.fixture()
def schedule_file_storage_config(tmpdir):
    """Return mock Config contaning a path to a valid schedule."""
    schedule_path = tmpdir.join(SCHEDULE_FILENAME)
    with open(schedule_path, "w", encoding="utf-8") as schedule_file:
        schedule_file.write(SCHEDULE_DATA)

    post_body_path = tmpdir.join(POST_BODY_FILENAME)
    with open(post_body_path, "w", encoding="utf-8") as post_body_file:
        post_body_file.write(POST_BODY)

    return MockConfig({"schedule_file": str(schedule_path)})
