import io
import re
from pathlib import Path

import yaml
from rich.console import Console

from hermes_cli.skin_engine import _build_skin_config, _load_skin_from_yaml


ROOT = Path(__file__).resolve().parents[1]
SKIN_PATH = ROOT / "skins" / "emh.yaml"
HEX_COLOR = re.compile(r"#[0-9A-Fa-f]{6}")
CANONICAL_WELCOME = "Please state the nature of your Hermes emergency."


def test_distribution_owns_emh_skin_directory():
    manifest = yaml.safe_load((ROOT / "distribution.yaml").read_text(encoding="utf-8"))

    assert "skins/" in manifest["distribution_owned"]


def test_emh_skin_loads_through_current_skin_engine():
    raw = _load_skin_from_yaml(SKIN_PATH)

    assert raw is not None
    assert raw["name"] == "emh"
    assert len(raw["colors"]) == 43
    assert all(HEX_COLOR.fullmatch(value) for value in raw["colors"].values())

    skin = _build_skin_config(raw)
    assert skin.name == "emh"
    assert skin.branding["welcome"] == CANONICAL_WELCOME


def test_emh_skin_banner_markup_renders():
    raw = _load_skin_from_yaml(SKIN_PATH)
    assert raw is not None
    skin = _build_skin_config(raw)
    output = io.StringIO()
    console = Console(file=output, force_terminal=True, color_system="truecolor", width=100)

    console.print(skin.banner_logo)
    console.print(skin.banner_hero)

    assert "EMERGENCY MEDICAL HERMES" in output.getvalue()
