# -*- coding: utf-8 -*-

import logging
from unittest.mock import patch

from click.testing import CliRunner

from slow_start_rewatch.__main__ import main
from slow_start_rewatch.exceptions import Abort, SlowStartRewatchException


@patch("slow_start_rewatch.__main__.App")
def test_run_successfully(mock_app):
    """Test launching the program without params."""
    runner = CliRunner()

    cli_result = runner.invoke(main)
    assert mock_app.return_value.run.call_count == 1
    assert cli_result.exit_code == 0
    assert logging.getLogger().getEffectiveLevel() == logging.CRITICAL


@patch("slow_start_rewatch.__main__.App")
def test_check_version(mock_app):
    """Test the launch with the ``--version`` option."""
    runner = CliRunner()

    cli_result = runner.invoke(main, ["--version"])
    assert cli_result.exit_code == 0
    assert "slow-start-rewatch, version" in cli_result.output
    assert mock_app.return_value.run.call_count == 0


@patch("slow_start_rewatch.__main__.App")
def test_debug(mock_app, request):
    """
    Test the launch with the ``--debug`` option.

    The logging level should be changed to ``DEBUG``.

    To avoid affecting other tests the logging level is changed back to the
    original value during the teardown.
    """
    logger = logging.getLogger()
    request.addfinalizer(lambda: logger.setLevel(logging.CRITICAL))

    assert logger.getEffectiveLevel() == logging.CRITICAL

    runner = CliRunner()
    cli_result = runner.invoke(main, ["--debug"])

    assert logger.getEffectiveLevel() == logging.DEBUG
    assert cli_result.exit_code == 0


@patch("slow_start_rewatch.__main__.App")
def test_handled_exception_with_hint(mock_app):
    """Test the output of a handled exception (with a hint)."""
    runner = CliRunner()
    mock_app.return_value.run.side_effect = SlowStartRewatchException(
        message="The cute app is pouting.",
        hint="Give her headpats.",
    )

    cli_result = runner.invoke(main)
    assert cli_result.exit_code == 1
    assert "pouting" in cli_result.output
    assert "headpats" in cli_result.output


@patch("slow_start_rewatch.__main__.App")
def test_handled_abort(mock_app):
    """Test the output of an aborted run (an exception without a hint)."""
    runner = CliRunner()
    mock_app.return_value.run.side_effect = Abort

    cli_result = runner.invoke(main)
    assert cli_result.exit_code == 130
    assert "aborted" in cli_result.output


@patch("slow_start_rewatch.__main__.App")
def test_unhandled_exception(mock_app):
    """Test the output of an unhandled exception."""
    runner = CliRunner()
    mock_app.return_value.run.side_effect = Exception("Reddit API is pouting.")

    cli_result = runner.invoke(main)
    assert cli_result.exit_code == 1
    assert "unexpected error" in cli_result.output
    assert "pouting" in cli_result.output
