# -*- coding: utf-8 -*-

from datetime import datetime
from unittest.mock import call, patch

import pytest

from slow_start_rewatch.exceptions import InvalidSchedule
from slow_start_rewatch.post import Post
from slow_start_rewatch.schedule.schedule import Schedule
from slow_start_rewatch.schedule.schedule_storage import (
    PostsData,
    ScheduleStorage,
)

SCHEDULE_DATA = """subreddit: anime
posts:
- name: episode_01
  submit_at: 2018-01-06 12:00:00
  title: Slow Start - Episode 1 Discussion
  body_template: episode_01.md
  navigation_scheduled: '-'
  navigation_submitted: '[ep 1]($link)'
  navigation_current: ep 1
  submission_id: 7okphp
- name: episode_02
  submit_at: 2018-01-13 12:00:00
  title: Slow Start - Episode 2 Discussion
  body_template: episode_02.md
  navigation_scheduled: '-'
  navigation_submitted: '[ep 2]($link)'
  navigation_current: ep 2
- name: episode_03
  submit_at: 2018-01-20 12:00:00
  title: Slow Start - Episode 3 Discussion
  body_template: episode_03.md
  navigation_scheduled: '-'
  navigation_submitted: '[ep 3]($link)'
  navigation_current: ep 3
"""

POST_BODY = """*Slow Start*, Episode 0

---

**Streams:**

* [Crunchyroll](https://www.crunchyroll.com/slow-start/episode-1-the-first-butterflies-759027)
* [VRV](https://vrv.co/watch/G69P1KQ0Y/Slow-Start:The-First-Butterflies)

---

**Show Information:**

* [MyAnimeList](https://myanimelist.net/anime/35540)
* [AniDB](http://anidb.net/perl-bin/animedb.pl?show=anime&aid=13160)
* [AniList](https://anilist.co/anime/98693/SlowStart)
* [Official Website](http://slow-start.com)
* [US Website](http://slowstart-usa.com/)
* [Twitter](https://twitter.com/slosta_anime)
* [US Facebook Page](https://www.facebook.com/SlowStartUSA/)

---

**Schedule:**

Date|Episode
-|-
Jan 6|$episode_01
Jan 13|$episode_02
Jan 20|$episode_03
"""  # noqa: E501


class ScheduleDummyStorage(ScheduleStorage):
    """Dummy `ScheduleStorage` class."""

    def __init__(self) -> None:
        """Initialize ScheduleDummyStorage."""
        super().__init__()

        self.test_invalid_date_format = False
        self.test_missing_data = False
        self.test_invalid_yaml = False
        self.skip_update_submitted_posts = False

    def load_schedule_data(self) -> str:
        """Load schedule data."""
        schedule_data = SCHEDULE_DATA

        if self.test_invalid_date_format:
            schedule_data = schedule_data.replace("2018-01-06", "6/1/2018")

        if self.test_missing_data:
            schedule_data = schedule_data.replace("subreddit: anime", "")

        if self.test_invalid_yaml:
            schedule_data = schedule_data.replace("- name: ", "  - name: ")

        return schedule_data

    def load_post_body(self, body_template_source: str) -> str:
        """Load a post body."""
        return POST_BODY.replace("Episode 0", "Episode {0}".format(
            body_template_source[9:10],
        ))

    def update_submitted_posts(
        self,
        posts_data: PostsData,
        schedule: Schedule,
    ) -> PostsData:
        """Populate the data with IDs of submitted posts."""
        if self.skip_update_submitted_posts:
            return posts_data

        return super().update_submitted_posts(posts_data, schedule)

    def save_schedule_data(self, schedule_data: str) -> None:
        """Save the schedule data."""


def test_load():
    """Test loading `Schedule` data."""
    schedule_storage = ScheduleDummyStorage()

    schedule = schedule_storage.load()

    assert schedule.subreddit == "anime"
    assert len(schedule.posts) == 3
    assert schedule.posts[1].title == "Slow Start - Episode 2 Discussion"
    assert "*Slow Start*, Episode 3" in schedule.posts[2].body_template


def test_load_with_errors():
    """Test loading `Schedule` data with errors."""
    schedule_storage = ScheduleDummyStorage()

    schedule_storage.test_invalid_date_format = True
    with pytest.raises(InvalidSchedule) as format_error:
        schedule_storage.load()

    # Comply with PT012: https://pypi.org/project/flake8-pytest-style/
    assert "invalid value" in str(format_error.value)  # noqa: WPS441

    schedule_storage.test_missing_data = True
    with pytest.raises(InvalidSchedule) as invalid_error:
        schedule_storage.load()

    assert "Incomplete" in str(invalid_error.value)  # noqa: WPS441

    schedule_storage.test_invalid_yaml = True
    with pytest.raises(InvalidSchedule) as incomplete_error:
        schedule_storage.load()

    assert "Failed to parse" in str(incomplete_error.value)  # noqa: WPS441


@patch.object(ScheduleDummyStorage, "save_schedule_data")
def test_save(mock_save_schedule_data, schedule):
    """
    Test saving Schedule data.

    Check that the saved YAML matches the loaded YAML when the update of
    submitted posts is skipped. Strict formatting of `SCHEDULE_DATA` is
    required.
    """
    schedule_storage = ScheduleDummyStorage()

    schedule_storage.skip_update_submitted_posts = True
    schedule_storage.save(schedule)

    assert mock_save_schedule_data.call_args == call(SCHEDULE_DATA)


def test_update_submitted_posts(schedule):
    """Test populating the Schedule data with IDs of submitted posts."""
    posts_data: PostsData = [
        {"name": "episode_{0}".format(post_id)} for post_id in range(1, 4)
    ]

    schedule_storage = ScheduleDummyStorage()

    schedule_storage.update_submitted_posts(posts_data, schedule)

    assert posts_data[0]["submission_id"] == "cute_id"
    assert "submission_id" not in posts_data[1]


@pytest.fixture()
def schedule():
    """
    Return mock `Schedule`.

    The first Post has `submission_id` filled in.
    """
    posts = [
        Post(
            name="episode_{0}".format(post_id),
            submit_at=datetime(2018, 1, 6, 17, 0, 0),
            subreddit="anime",
            title="Slow Start - Episode {0} Discussion".format(post_id),
            body_template="*Slow Start*, Episode {0}".format(post_id),
        ) for post_id in range(1, 4)
    ]
    posts[0].submission_id = "cute_id"

    return Schedule(subreddit="anime", posts=posts)
