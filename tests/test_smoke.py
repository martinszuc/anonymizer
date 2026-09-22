"""Smoke tests: the workspace installs and the offline guard is active."""

import socket

import pytest
from anonymizer.cli.main import main
from anonymizer.core import __version__


def test_core_exposes_version():
    assert __version__


def test_cli_version_flag(capsys):
    assert main(["--version"]) == 0
    assert capsys.readouterr().out.strip() == __version__


def test_network_is_blocked_during_tests():
    """pytest-socket must prevent any outbound connection (offline-only constraint)."""
    with pytest.raises(BaseException, match="socket"):
        socket.socket(socket.AF_INET, socket.SOCK_STREAM)
