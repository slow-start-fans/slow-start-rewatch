# -*- coding: utf-8 -*-

from typing import Optional

EXIT_CODE_SCRIPT_ABORTED = 130


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


class MissingLocalConfig(SlowStartRewatchException):
    """Indicates that the local config file does not exist."""

    def __init__(self):
        """Initialize MissingLocalConfig."""
        message = "Local config file not found."
        super().__init__(message)


class InvalidLocalConfig(SlowStartRewatchException):
    """Indicates an error in the local config file."""


class ConfigError(SlowStartRewatchException):
    """Indicates an error when accessing the config."""


class InvalidSchedule(SlowStartRewatchException):
    """Indicates an error in the data about scheduled posts."""


class MissingSchedule(SlowStartRewatchException):
    """Indicates that data about scheduled posts are missing."""


class MissingPost(SlowStartRewatchException):
    """Indicates that data about post are missing."""


class Abort(SlowStartRewatchException):
    """An internal signal that Ctrl+C has been pressed."""

    def __init__(self):
        """Initialize Abort."""
        message = "The program has been aborted."
        super().__init__(message, exit_code=EXIT_CODE_SCRIPT_ABORTED)


class AuthorizationError(SlowStartRewatchException):
    """Indicates an error during the authorization."""


class RedditError(SlowStartRewatchException):
    """Indicates an error when accessing Reddit API."""


class InvalidRefreshToken(SlowStartRewatchException):
    """Indicates the refresh token is corrupt and cannot be used to log in."""


class MissingRefreshToken(SlowStartRewatchException):
    """Indicates the saved refresh token was not found."""

    def __init__(self):
        """Initialize MissingRefreshToken."""
        message = "Refresh token not found."
        super().__init__(message)


class ImageNotFound(SlowStartRewatchException):
    """Indicates the post does not contain an image."""


class PostConversionError(SlowStartRewatchException):
    """Indicates an error when converting a post."""


class InvalidWikiLink(SlowStartRewatchException):
    """Indicates the Wiki source was not found."""
