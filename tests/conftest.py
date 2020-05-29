# -*- coding: utf-8 -*-

"""
This module is used to provide configuration, fixtures, and plugins for pytest.

It may be also used for extending doctest's context:
1. https://docs.python.org/3/library/doctest.html
2. https://docs.pytest.org/en/latest/doctest.html
"""

from dotty_dict import dotty

from slow_start_rewatch.config import Config


class MockConfig(Config):
    """Simplified version of the Config class."""

    def __init__(self, config_data=None) -> None:
        """Initialize MockConfig."""
        self.config = dotty(config_data)
