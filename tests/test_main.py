# -*- coding: utf-8 -*-

import logging

from click.testing import CliRunner

from slow_start_rewatch.__main__ import main


def test_run_successfully():
    """Test launching the program without params."""
    runner = CliRunner()

    cli_result = runner.invoke(main)
    assert cli_result.exit_code == 0
    assert logging.getLogger().getEffectiveLevel() == logging.CRITICAL


def test_check_version():
    """Test the launch with the ``--version`` option."""
    runner = CliRunner()

    cli_result = runner.invoke(main, ["--version"])
    assert cli_result.exit_code == 0
    assert "slow-start-rewatch, version" in cli_result.output


def test_debug(request):
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
