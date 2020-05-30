# -*- coding: utf-8 -*-

"""
This module is used to provide configuration, fixtures, and plugins for pytest.

It may be also used for extending doctest's context:
1. https://docs.python.org/3/library/doctest.html
2. https://docs.pytest.org/en/latest/doctest.html
"""

import os
from datetime import datetime

import pytest
from dotty_dict import dotty

from slow_start_rewatch.config import Config
from slow_start_rewatch.post import Post

TEST_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


class MockConfig(Config):
    """Simplified version of the Config class."""

    def __init__(self, config_data=None) -> None:
        """Initialize MockConfig."""
        self.config = dotty(config_data)


@pytest.fixture()
def post():
    """Return an example Post."""
    body = """*Slow Start*, Episode 1: The First Butterflies

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
        body=body,
    )
