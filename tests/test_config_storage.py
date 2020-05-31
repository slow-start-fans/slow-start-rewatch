# -*- coding: utf-8 -*-

import os
from unittest.mock import patch

from slow_start_rewatch.config_storage import ConfigStorage
from tests.conftest import REFRESH_TOKEN


def test_saving_to_existing_directory(tmpdir):
    """Test that the token is saved to an existing directory."""
    existing_path = tmpdir.join("reddit_token.dat")
    config_storage = ConfigStorage(existing_path)

    assert not os.path.exists(existing_path)

    config_storage.save_refresh_token(REFRESH_TOKEN)

    with open(existing_path) as token_file:
        assert token_file.read() == REFRESH_TOKEN


def test_saving_to_new_directory(tmpdir):
    """Test that a new directory is created before saving the token."""
    new_directory = tmpdir.join("new_directory")
    assert not os.path.exists(new_directory)

    new_path = new_directory.join("reddit_token.dat")
    config_storage = ConfigStorage(new_path)

    config_storage.save_refresh_token(REFRESH_TOKEN)

    assert os.path.exists(new_directory)

    with open(new_path) as token_file:
        assert token_file.read() == REFRESH_TOKEN


def test_saving_empty_token(tmpdir):
    """Test that an empty token is not saved."""
    refresh_token_file = tmpdir.join("reddit_token.dat")
    config_storage = ConfigStorage(refresh_token_file)

    config_storage.save_refresh_token(None)

    assert not os.path.exists(refresh_token_file)


def test_loading_existing_file(tmpdir):
    """Test that the token is loaded from the existing file."""
    refresh_token_file = tmpdir.join("reddit_token.dat")

    with open(refresh_token_file, "w") as token_file:
        token_file.write(REFRESH_TOKEN)

    config_storage = ConfigStorage(refresh_token_file)
    assert config_storage.load_refresh_token() == REFRESH_TOKEN


def test_loading_nonexistent_file(tmpdir):
    """Test that loading a nonexistent file returns ``None``."""
    refresh_token_file = tmpdir.join("reddit_token.dat")
    assert not os.path.exists(refresh_token_file)

    config_storage = ConfigStorage(refresh_token_file)
    assert config_storage.load_refresh_token() is None


def test_deleting_file(tmpdir):
    """
    Test deleting the token.

    The method for deleting is called twice to check that deleting
    a nonexistent file works fine as well.
    """
    refresh_token_file = tmpdir.join("reddit_token.dat")

    with open(refresh_token_file, "w") as token_file:
        token_file.write(REFRESH_TOKEN)

    assert os.path.exists(refresh_token_file)

    config_storage = ConfigStorage(refresh_token_file)
    config_storage.delete_refresh_token()
    assert not os.path.exists(refresh_token_file)

    with patch("os.remove") as mock_remove:
        config_storage.delete_refresh_token()
        assert mock_remove.call_count == 1
