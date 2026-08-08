import os
import urllib.request
from pathlib import Path

import pytest


def test_suite_uses_an_isolated_hermes_home():
    configured = Path(os.environ["HERMES_HOME"]).resolve()
    live_default = (Path.home() / ".hermes").resolve()

    assert configured != live_default
    assert configured.name == "hermes-home"
    assert configured.is_dir()


def test_network_guard_fails_closed_before_transport():
    assert getattr(urllib.request.urlopen, "__emh_network_guard__", False)

    with pytest.raises(RuntimeError, match="EMH test network access denied"):
        urllib.request.urlopen("https://hermes-agent.nousresearch.com/docs")
