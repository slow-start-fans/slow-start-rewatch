# -*- coding: utf-8 -*-

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest
from ruamel.yaml import YAML  # type: ignore

from slow_start_rewatch.exceptions import InvalidSchedule, MissingSchedule
from slow_start_rewatch.scheduler import Scheduler
from tests.conftest import TEST_ROOT_DIR, MockConfig

TEST_SCHEDULER_PATH = Path(TEST_ROOT_DIR).joinpath("test_scheduler")
VALID_POST_FILENAME = "scheduled_post.yml"
INVALID_POST_FILENAME = "scheduled_post_invalid.yml"
INCOMPLETE_POST_FILENAME = "scheduled_post_incomplete.yml"


@patch.object(Scheduler, "parse_post_from_yaml")
def test_load(  # noqa: WPS211
    mock_parse_post_from_yaml,
    scheduler_config,
    reddit,
    post,
):
    """Test loading of the scheduled post."""
    post.submit_at = datetime.now() + timedelta(minutes=1)
    mock_parse_post_from_yaml.return_value = post

    scheduler = Scheduler(scheduler_config)

    assert not scheduler.scheduled_post

    scheduler.load("cute_tester")

    assert scheduler.scheduled_post == post


@patch.object(Scheduler, "create_default")
@patch.object(Scheduler, "parse_post_from_yaml")
def test_load_with_exception(  # noqa: WPS211
    mock_parse_post_from_yaml,
    mock_create_default,
    scheduler_config,
    reddit,
    post,
):
    """Test loading of the scheduled post with error."""
    mock_parse_post_from_yaml.side_effect = FileNotFoundError

    scheduler = Scheduler(scheduler_config)

    with pytest.raises(MissingSchedule):
        scheduler.load("cute_tester")

    assert mock_create_default.call_count == 1


def test_parse_post_from_yaml(
    scheduler_config,
    reddit,
    post,
    post_files,
):
    """
    Test parsing of the scheduled post from YAML.

    1. A valid file

    2. An invalid file that cannot be parsed

    3. A file with missing fields
    """
    scheduler = Scheduler(scheduler_config)

    assert scheduler.parse_post_from_yaml(
        post_files[VALID_POST_FILENAME],
    ) == post

    with pytest.raises(InvalidSchedule) as invalid_error:
        scheduler.parse_post_from_yaml(
            post_files[INVALID_POST_FILENAME],
        )

    # Comply with PT012: https://pypi.org/project/flake8-pytest-style/
    assert "Failed to parse" in str(invalid_error.value)  # noqa: WPS441

    with pytest.raises(InvalidSchedule) as incomplete_error:
        scheduler.parse_post_from_yaml(
            post_files[INCOMPLETE_POST_FILENAME],
        )

    assert "Incomplete" in str(incomplete_error.value)  # noqa: WPS441


def test_create_default(
    reddit,
    tmpdir,
):
    """
    Test creating a sample source file.

    Check that all placeholders are substituted.

    Check the parsed post contains the expected fields.
    """
    scheduled_post_path = tmpdir.join("scheduled_post.yml")

    scheduler = Scheduler(
        MockConfig({"scheduled_post_file": str(scheduled_post_path)}),
    )

    assert not os.path.exists(scheduled_post_path)

    scheduler.create_default("cute_tester")

    with open(scheduled_post_path, "r") as scheduled_post_file:
        yaml_content = scheduled_post_file.read()

    assert "${" not in yaml_content

    yaml_data = YAML(typ="safe").load(yaml_content)

    assert yaml_data["subreddit"] == "u_cute_tester"
    assert yaml_data["submit_at"] > datetime.now()


@pytest.fixture()
def post_files(tmpdir):
    """Create temporary post YAML files and return their paths."""
    file_names = [
        VALID_POST_FILENAME,
        INVALID_POST_FILENAME,
        INCOMPLETE_POST_FILENAME,
    ]

    scheduled_post_paths = {}

    for file_name in file_names:
        scheduled_post_path = tmpdir.join(file_name)
        shutil.copyfile(
            TEST_SCHEDULER_PATH.joinpath(file_name),
            scheduled_post_path,
        )
        scheduled_post_paths[file_name] = scheduled_post_path

    return scheduled_post_paths


@pytest.fixture()
def scheduler_config(tmpdir):
    """Return mock Config contaning a path to a valid scheduled post."""
    scheduled_post_path = tmpdir.join(VALID_POST_FILENAME)

    shutil.copyfile(
        TEST_SCHEDULER_PATH.joinpath(VALID_POST_FILENAME),
        scheduled_post_path,
    )

    return MockConfig({"scheduled_post_file": str(scheduled_post_path)})
