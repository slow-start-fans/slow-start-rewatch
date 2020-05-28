# -*- coding: utf-8 -*-

from click.testing import CliRunner

from slow_start_rewatch.__main__ import main


def test_run_successfully():
    """Test launching the program."""
    runner = CliRunner()

    cli_result = runner.invoke(main)
    assert cli_result.exit_code == 0
