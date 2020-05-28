# -*- coding: utf-8 -*-

from click.testing import CliRunner

from slow_start_rewatch.__main__ import main


def test_run_successfully():
    """Test launching the program without params."""
    runner = CliRunner()

    cli_result = runner.invoke(main)
    assert cli_result.exit_code == 0


def test_check_version():
    """Test the launch with the ``--version`` option."""
    runner = CliRunner()

    cli_result = runner.invoke(main, ["--version"])
    assert cli_result.exit_code == 0
    assert "slow-start-rewatch, version" in cli_result.output
