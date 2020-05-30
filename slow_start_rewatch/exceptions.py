# -*- coding: utf-8 -*-

from typing import Optional


class SlowStartRewatchException(Exception):
    """An exception that slow_start_rewatch can handle."""

    def __init__(self, message: str, hint: Optional[str] = None, exit_code=1):
        """Initialize SlowStartRewatchException."""
        super().__init__(message)
        self.message = message
        self.hint = hint
        self.exit_code = exit_code

    def __str__(self):
        """Return string representation of the exception."""
        return self.message


class InvalidSchedule(SlowStartRewatchException):
    """Indicates an error in the data about scheduled posts."""


class MissingSchedule(SlowStartRewatchException):
    """Indicates that data about scheduled posts are missing."""
