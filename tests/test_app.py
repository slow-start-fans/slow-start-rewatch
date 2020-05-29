# -*- coding: utf-8 -*-

from slow_start_rewatch.app import App
from tests.conftest import MockConfig


def test_run_successfully(capsys):
    """Test that the App runs."""
    app = App(MockConfig())
    app.run()
    captured = capsys.readouterr()

    assert "Slow Start" in captured.out
