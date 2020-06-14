# -*- coding: utf-8 -*-

"""
This module is used to provide configuration, fixtures, and plugins for pytest.

It may be also used for extending doctest's context:
1. https://docs.python.org/3/library/doctest.html
2. https://docs.pytest.org/en/latest/doctest.html
"""

import os
from datetime import datetime
from typing import Optional
from unittest import mock

import pytest
from dotty_dict import dotty

from slow_start_rewatch.config import Config
from slow_start_rewatch.post import Post

TEST_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
HTTP_SERVER_HOSTNAME = "127.0.0.1"
HTTP_SERVER_PORT = 65000

OAUTH_CODE = "anime_girls_are_cute"
REFRESH_TOKEN = "moe_moe_kyun"  # noqa: S105

TEST_IMAGE_URL = "https://raw.githubusercontent.com/slow-start-fans/slow-start-rewatch/master/assets/happy_shion.gif"  # noqa: E501


class MockConfig(Config):
    """
    Simplified version of the Config class.

    The refresh token isn't stored permanently.
    """

    def __init__(self, config_data=None) -> None:
        """Initialize MockConfig."""
        self.config = dotty(config_data)
        self._refresh_token = None

    @property
    def refresh_token(self) -> Optional[str]:
        """Get the refresh token."""
        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, refresh_token) -> None:
        """Set the refresh token."""
        self._refresh_token = refresh_token


@pytest.fixture()
def post():
    """Return an example Post."""
    body_md = """*Slow Start*, Episode 1: The First Butterflies

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
"""  # noqa: E501

    return Post(
        submit_at=datetime(2018, 1, 6, 12, 0, 0),
        subreddit="anime",
        title="Slow Start - Episode 1 Discussion",
        body_md=body_md,
        submit_with_thumbnail=True,
    )


@pytest.fixture()
def reddit():
    """Return mock `Reddit` class."""
    mock_reddit = mock.Mock()
    mock_reddit.auth.scopes.return_value = ["headpat", "hug"]
    mock_reddit.auth.url.return_value = "cute_resource_locator"
    mock_reddit.auth.authorize.return_value = REFRESH_TOKEN
    mock_reddit.user.me.return_value.name = "cute_tester"

    return mock_reddit


@pytest.fixture()
def submission():
    """Return mock `Submission`."""
    mock_submission = mock.Mock()
    mock_submission.permalink = "slow_start_post_link"

    return mock_submission
