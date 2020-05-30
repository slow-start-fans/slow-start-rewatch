# -*- coding: utf-8 -*-

import os
import shutil
from pathlib import Path

import pytest

from slow_start_rewatch.exceptions import InvalidSchedule, MissingSchedule
from slow_start_rewatch.scheduler import Scheduler
from tests.conftest import TEST_ROOT_DIR, MockConfig

TEST_SCHEDULER_PATH = Path(TEST_ROOT_DIR).joinpath("test_scheduler")


def test_loading_existing_file(scheduler_config_valid, post):
    """Test loading the Post when configured with a valid file."""
    scheduler = Scheduler(scheduler_config_valid)

    assert not scheduler.scheduled_post

    scheduler.load("cute_tester")

    assert scheduler.scheduled_post == post


def test_loading_invalid_file(scheduler_config_invalid):
    """Test loading the Post when configured with a invalid file."""
    scheduler = Scheduler(scheduler_config_invalid)

    assert not scheduler.scheduled_post

    with pytest.raises(InvalidSchedule):
        scheduler.load("cute_tester")


def test_loading_nonexistent_file(scheduler_config_missing):
    """Test loading the Post when the source file is missing."""
    scheduler = Scheduler(scheduler_config_missing)

    scheduled_post_file = scheduler_config_missing["scheduled_post_file"]

    assert not os.path.exists(scheduled_post_file)

    with pytest.raises(MissingSchedule):
        scheduler.load("cute_tester")


@pytest.fixture()
def scheduler_config_valid(tmpdir):
    """Return mock Config contaning a path to a valid Scheduled Post."""
    scheduled_post_path = tmpdir.join("scheduled_post.yml")

    shutil.copyfile(
        TEST_SCHEDULER_PATH.joinpath("scheduled_post.yml"),
        scheduled_post_path,
    )

    return MockConfig({"scheduled_post_file": str(scheduled_post_path)})


@pytest.fixture()
def scheduler_config_invalid(tmpdir):
    """Return mock Config contaning a path to an invalid Scheduled Post."""
    scheduled_post_path = tmpdir.join("scheduled_post.yml")

    shutil.copyfile(
        TEST_SCHEDULER_PATH.joinpath("scheduled_post_invalid.yml"),
        scheduled_post_path,
    )

    return MockConfig({"scheduled_post_file": str(scheduled_post_path)})


@pytest.fixture()
def scheduler_config_missing(tmpdir):
    """Return mock Config contaning a path to a missing Scheduled Post."""
    scheduled_post_path = tmpdir.join("scheduled_post.yml")

    return MockConfig({"scheduled_post_file": str(scheduled_post_path)})
