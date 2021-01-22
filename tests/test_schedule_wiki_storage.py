# -*- coding: utf-8 -*-

from pathlib import Path
from unittest.mock import MagicMock, Mock, PropertyMock

import pytest
from praw.models.reddit.subreddit import SubredditWiki
from prawcore.exceptions import Forbidden, NotFound, PrawcoreException

from slow_start_rewatch.exceptions import (
    InvalidWikiLink,
    MissingPost,
    MissingSchedule,
    RedditError,
)
from slow_start_rewatch.schedule.schedule_wiki_storage import (
    ScheduleWikiStorage,
)
from tests.conftest import TEST_ROOT_DIR, MockConfig
from tests.test_schedule_storage import POST_BODY, SCHEDULE_DATA

wiki = SubredditWiki

TEST_SCHEDULE_PATH = Path(TEST_ROOT_DIR).joinpath("test_schedule")
SCHEDULE_FILENAME = "schedule.yml"
POST_BODY_FILENAME = "episode_01.md"


def test_load_schedule_data(schedule_wiki_storage_config, reddit_with_wiki):
    """Test loading of the Schedule data from the wiki."""
    schedule_wiki_storage = ScheduleWikiStorage(
        schedule_wiki_storage_config,
        reddit_with_wiki,
    )

    schedule_data = schedule_wiki_storage.load_schedule_data()

    assert schedule_data == SCHEDULE_DATA


def test_load_schedule_data_not_found(reddit_with_wiki):
    """Test loading of the Schedule data from the nonexistent wiki."""
    config = MockConfig({
        "schedule_wiki_url": "/r/anime/wiki/not-found",
    })

    schedule_wiki_storage = ScheduleWikiStorage(config, reddit_with_wiki)

    with pytest.raises(MissingSchedule) as missing_schedule_error:
        schedule_wiki_storage.load_schedule_data()

    # Comply with PT012: https://pypi.org/project/flake8-pytest-style/
    error_message = str(missing_schedule_error.value)  # noqa: WPS441

    assert "wiki page not found" in error_message
    assert "/r/anime/wiki/not-found" in error_message


def test_load_schedule_data_forbidden(reddit_with_wiki):
    """Test loading of the Schedule data from the inaccessible wiki."""
    config = MockConfig({
        "schedule_wiki_url": "/r/anime/wiki/forbidden",
    })

    schedule_wiki_storage = ScheduleWikiStorage(config, reddit_with_wiki)

    with pytest.raises(MissingSchedule) as missing_schedule_error:
        schedule_wiki_storage.load_schedule_data()

    # Comply with PT012: https://pypi.org/project/flake8-pytest-style/
    error_message = str(missing_schedule_error.value)  # noqa: WPS441

    assert "permissions to access" in error_message
    assert "/r/anime/wiki/forbidden" in error_message


def test_load_post_body(schedule_wiki_storage_config, reddit_with_wiki):
    """Test loading of the Post body from the wiki."""
    schedule_wiki_storage = ScheduleWikiStorage(
        schedule_wiki_storage_config,
        reddit_with_wiki,
    )

    post_body = schedule_wiki_storage.load_post_body("episode_01")

    assert post_body == POST_BODY


def test_load_post_body_not_found(reddit_with_wiki):
    """Test loading of the Post body from the nonexistent wiki."""
    config = MockConfig({
        "schedule_wiki_url": "/r/anime/wiki/not-found",
    })

    schedule_wiki_storage = ScheduleWikiStorage(config, reddit_with_wiki)

    with pytest.raises(MissingPost) as missing_post_error:
        schedule_wiki_storage.load_post_body("episode_01")

    # Comply with PT012: https://pypi.org/project/flake8-pytest-style/
    error_message = str(missing_post_error.value)  # noqa: WPS441

    assert "wiki page not found" in error_message
    assert "/r/anime/wiki/not-found/episode_01" in error_message


def test_load_post_body_forbidden(reddit_with_wiki):
    """Test loading of the Post body from the inaccessible wiki."""
    config = MockConfig({
        "schedule_wiki_url": "/r/anime/wiki/forbidden",
    })

    schedule_wiki_storage = ScheduleWikiStorage(config, reddit_with_wiki)

    with pytest.raises(MissingPost) as missing_post_error:
        schedule_wiki_storage.load_post_body("episode_01")

    # Comply with PT012: https://pypi.org/project/flake8-pytest-style/
    error_message = str(missing_post_error.value)  # noqa: WPS441

    assert "permissions to access" in error_message
    assert "/r/anime/wiki/forbidden/episode_01" in error_message


def test_save_schedule_data(schedule_wiki_storage_config, reddit_with_wiki):
    """
    Test saving of the Schedule data to the wiki.

    Check that the content is indented by 4 spaces.
    """
    schedule_wiki_storage = ScheduleWikiStorage(
        schedule_wiki_storage_config,
        reddit_with_wiki,
    )

    schedule_wiki_storage.save_schedule_data(SCHEDULE_DATA)

    wiki_edit = reddit_with_wiki.subreddit().wiki["slow-start-rewatch"].edit

    assert "anime\n    posts:" in wiki_edit.call_args[1]["content"]
    assert wiki_edit.call_args[1]["reason"] == "Rewatch Update"


def test_save_schedule_data_error(reddit_with_wiki):
    """Test saving of the Schedule data to the wiki with en error."""
    config = MockConfig({
        "schedule_wiki_url": "/r/anime/wiki/not-found",
    })

    schedule_wiki_storage = ScheduleWikiStorage(config, reddit_with_wiki)

    with pytest.raises(RedditError) as reddit_error:
        schedule_wiki_storage.save_schedule_data(SCHEDULE_DATA)

    # Comply with PT012: https://pypi.org/project/flake8-pytest-style/
    error_message = str(reddit_error.value)  # noqa: WPS441

    assert "Failed to update" in error_message
    assert "/r/anime/wiki/not-found" in error_message


def test_invalid_config(reddit_with_wiki):
    """Test initializing `ScheduleWikiStorage` with invalid config."""
    config = MockConfig({"schedule_wiki_url": None})

    with pytest.raises(RuntimeError):
        ScheduleWikiStorage(config, reddit_with_wiki)

    invalid_wiki_url = "/r/anime/slow-start-rewatch"

    config["schedule_wiki_url"] = invalid_wiki_url

    with pytest.raises(InvalidWikiLink) as invalid_wiki_link_error:
        ScheduleWikiStorage(config, reddit_with_wiki)

    # Comply with PT012: https://pypi.org/project/flake8-pytest-style/
    error_message = str(invalid_wiki_link_error.value)  # noqa: WPS441

    assert invalid_wiki_url in error_message


@pytest.fixture()
def schedule_wiki_storage_config(tmpdir):
    """Return mock Config contaning a wiki URL."""
    return MockConfig({
        "schedule_wiki_url": "/r/anime/wiki/slow-start-rewatch",
    })


@pytest.fixture()
def reddit_with_wiki():
    """Return mock `Reddit` class with a mock wiki page."""
    reddit = Mock()

    wiki_page_schedule = Mock()
    wiki_page_schedule.content_md = SCHEDULE_DATA

    wiki_page_post_body = Mock()
    wiki_page_post_body.content_md = POST_BODY

    wiki_page_not_found = Mock()
    type(wiki_page_not_found).content_md = PropertyMock(
        side_effect=NotFound(response=MagicMock()),
    )
    type(wiki_page_not_found).edit = PropertyMock(
        side_effect=PrawcoreException,
    )

    wiki_page_forbidden = Mock()
    type(wiki_page_forbidden).content_md = PropertyMock(
        side_effect=Forbidden(response=MagicMock()),
    )

    reddit.subreddit().wiki = {
        "slow-start-rewatch": wiki_page_schedule,
        "slow-start-rewatch/episode_01": wiki_page_post_body,
        "not-found": wiki_page_not_found,
        "not-found/episode_01": wiki_page_not_found,
        "forbidden": wiki_page_forbidden,
        "forbidden/episode_01": wiki_page_forbidden,
    }

    return reddit
