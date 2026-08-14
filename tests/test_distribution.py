import re
from pathlib import Path

import pytest
import yaml
from hermes_cli.profile_distribution import DistributionError, check_hermes_requires, read_manifest


ROOT = Path(__file__).parents[1]

REQUIRED_SKILLS = {
    "emh-triage": "skills/emh-triage/SKILL.md",
    "emh-memory-diagnostics": "skills/emh-memory-diagnostics/SKILL.md",
    "emh-kanban-diagnostics": "skills/emh-kanban-diagnostics/SKILL.md",
    "emh-plugin-diagnostics": "skills/emh-plugin-diagnostics/SKILL.md",
    "emh-gateway-diagnostics": "skills/emh-gateway-diagnostics/SKILL.md",
    "emh-provider-diagnostics": "skills/emh-provider-diagnostics/SKILL.md",
    "emh-profile-session-skill-diagnostics": "skills/emh-profile-session-skill-diagnostics/SKILL.md",
    "emh-release-intelligence": "skills/emh-release-intelligence/SKILL.md",
    "emh-interface-diagnostics": "skills/emh-interface-diagnostics/SKILL.md",
    "emh-tool-runtime-diagnostics": "skills/emh-tool-runtime-diagnostics/SKILL.md",
    "emh-environment-diagnostics": "skills/emh-environment-diagnostics/SKILL.md",
    "emh-update-recovery": "skills/emh-update-recovery/SKILL.md",
    "emh-nightly-self-check": "skills/emh-nightly-self-check/SKILL.md",
    "emh-orientation": "skills/emh-orientation/SKILL.md",
    "emh-rescue-media": "skills/emh-rescue-media/SKILL.md",
    "emh-reddit-json": "skills/emh-reddit-json/SKILL.md",
}
EXPECTED_SKILL_VERSIONS = {
    name: "0.2.0" if name in {
        "emh-memory-diagnostics",
        "emh-kanban-diagnostics",
        "emh-plugin-diagnostics",
        "emh-gateway-diagnostics",
        "emh-provider-diagnostics",
        "emh-profile-session-skill-diagnostics",
        "emh-interface-diagnostics",
        "emh-tool-runtime-diagnostics",
        "emh-environment-diagnostics",
        "emh-update-recovery",
        "emh-nightly-self-check",
        "emh-orientation",
        "emh-rescue-media",
        "emh-reddit-json",
    } else "0.1.0"
    for name in REQUIRED_SKILLS
}
REQUIRED_REFERENCES = (
    "skills/emh-triage/references/evidence-and-source-policy.md",
    "skills/emh-triage/references/safety-and-redaction.md",
    "skills/emh-triage/references/subsystem-map.md",
)
RESPONSE_REFERENCE = "skills/emh-triage/references/response-templates.md"
REQUIRED_SECTIONS = ("## Workflow", "## Safety boundaries", "## Pitfalls", "## Verification")
CASE_LABELS = (
    "Complaint",
    "Vitals",
    "Differential diagnosis",
    "Confirmed diagnosis",
    "Treatment",
    "Post-treatment verification",
    "Discharge summary or escalation packet",
)
EVIDENCE_LABELS = (
    "Observed",
    "Reproduced",
    "Confirmed in installed source",
    "Officially documented",
    "Known upstream fix",
    "Hypothesis",
)


def test_manifest_has_required_metadata_and_owned_paths():
    manifest = yaml.safe_load((ROOT / "distribution.yaml").read_text(encoding="utf-8"))

    assert manifest["name"] == "emh"
    assert manifest["version"] == "0.2.9"
    assert manifest["author"] == "Jonathan Rivera"
    assert manifest["license"] == "MIT"
    assert manifest["hermes_requires"] == ">=0.14.0"
    assert manifest["distribution_owned"] == ["SOUL.md", "skills/", "skins/"]
    assert manifest["skills"] == list(REQUIRED_SKILLS)
    assert "config.yaml" not in manifest
    assert not manifest.get("env_requires")


def test_source_manifest_records_version_install_and_release_provenance():
    source = yaml.safe_load(
        (ROOT / "skills/emh-triage/references/source-manifest.json").read_text(
            encoding="utf-8"
        )
    )

    assert source["retrieved_at"].endswith("Z")
    assert source["installed"]["version"] == "0.20.0"
    assert source["installed"]["install_method"] == "git"
    assert source["installed"]["source_commit"] == (
        "01a1037d1e6d7b6eb96a786ef282c3aea4818194"
    )
    assert source["installed"]["dirty"] is True
    assert "filenames" not in source["installed"]
    assert source["latest_official_release"] == {
        "tag": "v2026.8.3",
        "version": "0.20.0",
        "url": "https://github.com/NousResearch/hermes-agent/releases/tag/v2026.8.3",
        "published_at": "2026-08-03T16:57:52Z",
    }
    assert "https://hermes-agent.nousresearch.com/docs" in source["official_sources"]
    assert "https://github.com/NousResearch/hermes-agent/releases/latest" in source[
        "official_sources"
    ]


def test_installed_distribution_loader_validates_manifest_and_version_requirement():
    manifest = read_manifest(ROOT)

    assert manifest is not None
    assert manifest.name == "emh"
    assert manifest.version == "0.2.9"
    assert manifest.hermes_requires == ">=0.14.0"
    assert manifest.distribution_owned == ["SOUL.md", "skills", "skins"]
    check_hermes_requires(manifest.hermes_requires, "0.20.0")

    with pytest.raises(DistributionError):
        check_hermes_requires(manifest.hermes_requires, "0.13.9")


def _skill_frontmatter(path: Path) -> tuple[dict, str]:
    content = path.read_text(encoding="utf-8")
    assert content.startswith("---\n"), f"missing YAML frontmatter: {path}"
    _, frontmatter, body = content.split("---", 2)
    parsed = yaml.safe_load(frontmatter)
    assert isinstance(parsed, dict), f"frontmatter is not a mapping: {path}"
    return parsed, body


def _has_markdown_heading(body: str, expected: str) -> bool:
    in_fence = False
    fence_char = ""
    fence_length = 0
    for line in body.splitlines():
        if in_fence:
            closing = re.fullmatch(r" {0,3}([`~]{3,})\s*", line)
            if (
                closing
                and closing.group(1)[0] == fence_char
                and len(closing.group(1)) >= fence_length
            ):
                in_fence = False
            continue
        opening = re.match(r"^ {0,3}([`~]{3,})(?:.*)$", line)
        if opening:
            in_fence = True
            fence_char = opening.group(1)[0]
            fence_length = len(opening.group(1))
            continue
        if line == expected:
            return True
    return False


def test_required_portable_skills_and_references_exist():
    for path in [
        *(ROOT / relative for relative in REQUIRED_SKILLS.values()),
        *(ROOT / relative for relative in REQUIRED_REFERENCES),
        ROOT / RESPONSE_REFERENCE,
    ]:
        assert path.is_file(), f"required distribution content is missing: {path.relative_to(ROOT)}"


def test_shared_response_reference_preserves_concise_order_and_safety_proof():
    reference = (ROOT / RESPONSE_REFERENCE).read_text(encoding="utf-8")
    headings = [
        "## What I found",
        "## What it means",
        "## Safest next step",
        "## Permission needed: Yes/No",
        "## Technical details",
    ]
    positions = [reference.index(heading) for heading in headings]
    assert positions == sorted(positions)
    for phrase in (
        "evidence labels",
        "citations",
        "commands and exit status",
        "version/profile scope",
        "stage classification",
        "IDs, timestamps, and errors",
        "uncertainty and falsification",
        "redacted escalation support data",
        "never hidden below details",
        "exact, target-specific, and just-in-time",
        "raw secrets",
        "raw logs",
        "private identifiers",
        "calm and non-blaming",
        "corrective quips",
    ):
        assert phrase.lower() in reference.lower()
    for template in (
        "Intake",
        "Check in progress",
        "Diagnosis found",
        "More evidence needed",
        "Approval request",
        "Escalation/support packet",
    ):
        assert template in reference


def test_soul_makes_concise_presentation_canonical_and_case_structure_internal():
    soul = (ROOT / "SOUL.md").read_text(encoding="utf-8")
    assert "response-templates.md" in soul
    assert "internal/support-detail structure" in soul
    assert "every normal answer follows the concise response order" in soul
    assert "Permission needed: Yes/No" in soul


def test_readme_uses_canonical_profile_title_and_clone_url():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert readme.splitlines()[0] == "# EMH — A Hermes Diagnostic Profile"
    assert "git clone https://github.com/AtlasOmnia/EMH-A-Hermes-Diagnostic-Profile.git" in readme


def test_public_start_here_and_single_safety_statement_are_obvious():
    for relative in ("README.md", "docs/user-guide.md"):
        content = (ROOT / relative).read_text(encoding="utf-8")
        start = content.index("## Start here")
        reference = content.index("## ", start + len("## Start here"))
        start_block = content[start:reference]
        assert "1." in start_block
        assert "install" in start_block.lower()
        assert "start" in start_block.lower()
        assert "setup" in start_block.lower()
        assert "describe the problem" in start_block.lower()
        assert "consent" in start_block.lower()
        assert "read-only" in start_block.lower()
        assert "before changing configuration, installing anything, contacting an external service, or sending data, it shows the exact action and asks" in content.lower()


def test_public_version_and_weekly_changelog_contract():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    manifest = yaml.safe_load((ROOT / "distribution.yaml").read_text(encoding="utf-8"))
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert manifest["version"] == "0.2.9"
    assert "distribution version: `0.2.9`" in readme.lower()
    assert "newest entries are public release notes" in changelog.lower()
    assert "weekly" in changelog.lower()
    assert "unreleased" in changelog.lower()
    assert "## 0.2.9" in changelog
    assert "concise" in changelog.lower()


def test_all_portable_skills_have_public_contract_frontmatter_and_sections():
    for name, relative in REQUIRED_SKILLS.items():
        frontmatter, body = _skill_frontmatter(ROOT / relative)
        assert frontmatter["name"] == name
        assert frontmatter["version"] == EXPECTED_SKILL_VERSIONS[name]
        assert frontmatter["author"] == "Jonathan Rivera"
        assert frontmatter["license"] == "MIT"
        assert frontmatter["platforms"] == ["linux", "macos", "windows"]
        assert isinstance(frontmatter["description"], str)
        assert frontmatter["description"].startswith("Use when ")
        assert len(frontmatter["description"]) <= 240
        sections = REQUIRED_SECTIONS if frontmatter["version"] == "0.1.0" else (
            "## Overview",
            "## When to Use",
            "## Evidence collection workflow",
            "## Decision tree",
            "## Exact commands and tool calls",
            "## Safety and approval boundaries",
            "## Common pitfalls and recovery",
            "## Verification checklist",
            "## Escalation packet requirements",
        )
        for section in sections:
            assert _has_markdown_heading(body, section), f"{section} missing from {relative}"
        if frontmatter["version"] == "0.2.0":
            hermes = frontmatter["metadata"]["hermes"]
            assert hermes["tags"]
            assert hermes["related_skills"]
        assert all(label in body for label in CASE_LABELS)
        assert all(label in body for label in EVIDENCE_LABELS)


def test_readme_documents_exact_inventory_and_mixed_version_policy():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    lower = readme.lower()

    assert "distribution version: `0.2.9`" in lower
    assert all(f"`{name}`" in readme for name in REQUIRED_SKILLS)
    assert "untouched v0.1 skills remain at `0.1.0`" in lower
    assert "fourteen v0.2 skills are `0.2.0`" in lower
    assert "two untouched v0.1 skills remain at `0.1.0`" in lower


def test_triage_references_cover_required_portable_safety_contract():
    combined = "\n".join(
        (ROOT / relative).read_text(encoding="utf-8") for relative in REQUIRED_REFERENCES
    )
    for label in CASE_LABELS + EVIDENCE_LABELS:
        assert label in combined
    for phrase in (
        "live runtime",
        "installed source",
        "version-matched release notes",
        "current official docs",
        "Known upstream fix",
        "GitHub-ready",
        "redact",
        "backup",
        "stable non-secret",
    ):
        assert phrase.lower() in combined.lower()


def test_official_source_index_covers_every_authoritative_subsystem_source():
    index = (ROOT / "skills/emh-triage/references/official-source-index.md").read_text(
        encoding="utf-8"
    )
    urls = (
        "https://hermes-agent.nousresearch.com/docs",
        "https://hermes-agent.nousresearch.com/docs/user-guide/profile-distributions",
        "https://hermes-agent.nousresearch.com/docs/reference/profile-commands",
        "https://hermes-agent.nousresearch.com/docs/user-guide/profiles",
        "https://hermes-agent.nousresearch.com/docs/user-guide/features/memory",
        "https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban",
        "https://hermes-agent.nousresearch.com/docs/user-guide/features/plugins",
        "https://hermes-agent.nousresearch.com/docs/developer-guide/plugins",
        "https://hermes-agent.nousresearch.com/docs/developer-guide/desktop-plugin-sdk",
        "https://hermes-agent.nousresearch.com/docs/user-guide/messaging/",
        "https://hermes-agent.nousresearch.com/docs/integrations/providers",
        "https://hermes-agent.nousresearch.com/docs/user-guide/sessions",
        "https://hermes-agent.nousresearch.com/docs/user-guide/features/skills",
        "https://hermes-agent.nousresearch.com/docs/user-guide/features/tools",
        "https://hermes-agent.nousresearch.com/docs/reference/tools-reference",
        "https://hermes-agent.nousresearch.com/docs/reference/cli-commands",
        "https://hermes-agent.nousresearch.com/docs/reference/environment-variables",
        "https://hermes-agent.nousresearch.com/docs/user-guide/tui",
        "https://hermes-agent.nousresearch.com/docs/user-guide/desktop",
        "https://github.com/NousResearch/hermes-agent/releases/latest",
        "https://api.github.com/repos/NousResearch/hermes-agent/releases/latest",
    )
    assert all(url in index for url in urls)
    assert "Officially documented" in index
    assert "EMH Recommendation" in index
