from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOUL = ROOT / "SOUL.md"
README = ROOT / "README.md"
CANONICAL_OPENING = "Please state the nature of your Hermes emergency."


def test_soul_uses_canonical_opening_line():
    lines = SOUL.read_text(encoding="utf-8").splitlines()

    assert lines[2] == CANONICAL_OPENING


def test_soul_defines_restrained_holographic_bedside_manner():
    soul = SOUL.read_text(encoding="utf-8")

    assert "## Holographic bedside manner" in soul
    assert "I'm a doctor, not a mechanic. I diagnose Hermes, not engines." in soul
    assert "First, do no harm—especially to a working configuration." in soul
    assert "I'm a Hermes doctor, not your physician." in soul
    assert "Use the EMH voice sparingly" in soul
    assert "Do not use corrective quips during first-run, missing-information, credential, possible-data-loss, or recovery-failure situations" in soul
    assert "I'm a hologram, not a clairvoyant. Please provide the vitals." not in soul
    assert "The patient is stable. Try not to reconfigure it unsupervised." not in soul
    assert "redirect" in soul.lower()


def test_readme_invocation_uses_canonical_opening_line():
    readme = README.read_text(encoding="utf-8")

    assert f'-q "{CANONICAL_OPENING}"' in readme
