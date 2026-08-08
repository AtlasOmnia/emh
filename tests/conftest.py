import os
import socket
import tempfile
import urllib.request
from pathlib import Path

import pytest


_SESSION_ROOT = Path(tempfile.mkdtemp(prefix="emh-tests-"))
_ISOLATED_HERMES_HOME = _SESSION_ROOT / "hermes-home"
_ISOLATED_HERMES_HOME.mkdir(mode=0o700)
os.environ["HERMES_HOME"] = str(_ISOLATED_HERMES_HOME)


def _deny_network(*_args, **_kwargs):
    raise RuntimeError("EMH test network access denied; inject a fake transport")


setattr(_deny_network, "__emh_network_guard__", True)
urllib.request.urlopen = _deny_network
socket.create_connection = _deny_network
socket.getaddrinfo = _deny_network
socket.socket.connect = _deny_network
socket.socket.connect_ex = _deny_network


@pytest.fixture(autouse=True)
def isolate_live_hermes_state(monkeypatch):
    """Keep every test away from the active Hermes home and live networking."""
    monkeypatch.setenv("HERMES_HOME", str(_ISOLATED_HERMES_HOME))
    yield
