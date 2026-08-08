import re
from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]
SKILLS_ROOT = ROOT / "skills"
EXPECTED_VERSIONS = {
    "emh-triage": "0.1.0",
    "emh-memory-diagnostics": "0.1.0",
    "emh-kanban-diagnostics": "0.1.0",
    "emh-plugin-diagnostics": "0.1.0",
    "emh-gateway-diagnostics": "0.1.0",
    "emh-provider-diagnostics": "0.1.0",
    "emh-profile-session-skill-diagnostics": "0.1.0",
    "emh-release-intelligence": "0.1.0",
    "emh-interface-diagnostics": "0.2.0",
    "emh-tool-runtime-diagnostics": "0.2.0",
    "emh-environment-diagnostics": "0.2.0",
    "emh-update-recovery": "0.2.0",
}


def read_frontmatter(path: Path) -> tuple[dict, str]:
    content = path.read_text(encoding="utf-8")
    assert content.startswith("---\n"), f"frontmatter must start at byte zero: {path}"
    _, frontmatter, body = content.split("---", 2)
    parsed = yaml.safe_load(frontmatter)
    assert isinstance(parsed, dict), f"frontmatter must be a mapping: {path}"
    return parsed, body


def test_exact_skill_inventory_and_intentional_mixed_versions():
    actual = {
        path.parent.name: read_frontmatter(path)[0]["version"]
        for path in sorted(SKILLS_ROOT.glob("*/SKILL.md"))
    }

    assert actual == EXPECTED_VERSIONS
    assert all(version == "0.1.0" for name, version in actual.items() if name.startswith("emh-") and name not in {
        "emh-interface-diagnostics",
        "emh-tool-runtime-diagnostics",
        "emh-environment-diagnostics",
        "emh-update-recovery",
    })
    assert all(actual[name] == "0.2.0" for name in (
        "emh-interface-diagnostics",
        "emh-tool-runtime-diagnostics",
        "emh-environment-diagnostics",
        "emh-update-recovery",
    ))


def test_v02_frontmatter_matches_public_skill_contract():
    for name in (
        "emh-interface-diagnostics",
        "emh-tool-runtime-diagnostics",
        "emh-environment-diagnostics",
        "emh-update-recovery",
    ):
        path = SKILLS_ROOT / name / "SKILL.md"
        metadata, body = read_frontmatter(path)
        assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", metadata["name"])
        assert metadata["name"] == name
        assert metadata["description"].startswith("Use when ")
        assert metadata["version"] == "0.2.0"
        assert metadata["author"] == "Jonathan Rivera"
        assert metadata["license"] == "UNLICENSED"
        assert metadata["platforms"] == ["linux", "macos", "windows"]
        hermes = metadata["metadata"]["hermes"]
        assert hermes["tags"]
        assert hermes["related_skills"]
        assert body.strip()


V02_SKILLS = (
    "emh-interface-diagnostics",
    "emh-tool-runtime-diagnostics",
    "emh-environment-diagnostics",
    "emh-update-recovery",
)
REQUIRED_SECTIONS = (
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
EVIDENCE_LABELS = (
    "Observed",
    "Reproduced",
    "Confirmed in installed source",
    "Officially documented",
    "Known upstream fix",
    "Hypothesis",
)


def skill_body(name: str) -> str:
    return read_frontmatter(SKILLS_ROOT / name / "SKILL.md")[1]


def section(body: str, heading: str, *, level: int = 2) -> str:
    marker = f"{'#' * level} {heading}"
    assert marker in body, f"missing section: {marker}"
    remainder = body.split(marker, 1)[1]
    next_heading = re.search(rf"^#{{1,{level}}} ", remainder, flags=re.MULTILINE)
    return remainder[: next_heading.start()] if next_heading else remainder


def read_only_allowlist(name: str) -> tuple[str, ...]:
    commands = section(skill_body(name), "Read-only allowlist", level=3)
    return tuple(re.findall(r"^- `([^`]+)`$", commands, flags=re.MULTILINE))


def test_each_v02_skill_has_complete_diagnostic_safety_contract():
    for name in V02_SKILLS:
        body = skill_body(name)
        assert all(section in body for section in REQUIRED_SECTIONS)
        assert "Don't use for" in body
        assert all(body.count(label) >= 1 for label in EVIDENCE_LABELS)
        assert "current runtime and installed source outrank generic guidance" in body
        assert "official docs are authoritative current documentation" in body
        assert "Read-only first" in body
        assert "explicit approval" in body
        assert "verified backup" in body
        assert "rollback" in body
        assert "Never silently" in body


def test_each_v02_skill_defines_bounded_escalation_packet_fields():
    required_fields = (
        "installed version",
        "platform",
        "reproduction",
        "expected behavior",
        "actual behavior",
        "minimal evidence",
        "residual question",
    )
    for name in V02_SKILLS:
        body = skill_body(name).lower()
        assert all(field in body for field in required_fields)
        assert "redact" in body
        assert "private" in body
        assert "raw logs" in body


def test_v02_triggers_counter_triggers_and_domain_layers_are_precise():
    expected_terms = {
        "emh-interface-diagnostics": (
            "classic cli",
            "prompt_toolkit",
            "tui",
            "node.js",
            "tty",
            "keybindings",
            "json-rpc",
            "desktop",
            "electron main process",
            "preload/ipc bridge",
            "react renderer",
            "hermes serve",
            "cdp",
            "provider",
            "gateway",
            "profile",
            "plugin",
            "tool",
            "backend",
        ),
        "emh-tool-runtime-diagnostics": (
            "discovery",
            "registration",
            "requirement",
            "check_fn",
            "toolset resolution",
            "schema exposure",
            "malformed",
            "denied",
            "dispatch",
            "handler",
            "execution backend",
            "result shaping",
            "truncation",
            "fresh session",
        ),
        "emh-environment-diagnostics": (
            "host/runtime environment",
            "execution environment",
            "macos",
            "linux",
            "native windows",
            "wsl",
            "local",
            "docker",
            "ssh",
            "modal",
            "daytona",
            "vercel sandbox",
            "singularity",
            "permissions",
            "network",
            "process",
            "persistence",
            "artifact location",
        ),
        "emh-update-recovery": (
            "source/install identification",
            "readiness",
            "verified backup",
            "rollback",
            "lock/process",
            "source acquisition",
            "dependency",
            "config migration",
            "restart",
            "post-update verification",
            "source_status.py --offline",
        ),
    }

    for name, terms in expected_terms.items():
        body = skill_body(name).lower()
        assert all(term in body for term in terms), name
        when_to_use = section(skill_body(name), "When to Use").lower()
        assert "don't use for:" in when_to_use
        assert len(when_to_use.split("don't use for:", 1)[1].strip()) >= 120


def test_v02_read_only_allowlists_are_exact_and_mutations_are_separate():
    expected = {
        "emh-interface-diagnostics": (
            "hermes --help",
            "hermes --version",
            "hermes status --all",
            "node --version",
            "hermes logs -n 50 --component cli --level WARNING",
            "hermes logs desktop -n 50 --level WARNING",
            'browser_cdp(method="Target.getTargets", params={})',
            'browser_cdp(method="Runtime.evaluate", params={"expression":"document.title","returnByValue":true}, target_id="<renderer-target-id>")',
            'computer_use(action="capture", mode="som", app="Hermes")',
        ),
        "emh-tool-runtime-diagnostics": (
            "hermes --version",
            "hermes status --all",
            "hermes tools --summary",
            "hermes tools list --platform cli",
            "hermes logs -n 50 --component tools --level WARNING",
            'tool_search(query="<capability>", limit=5)',
            'tool_describe(name="<exact-tool-name>")',
        ),
        "emh-environment-diagnostics": (
            "hermes --version",
            "hermes status --all",
            "hermes tools list --platform cli",
            'terminal(command="python -c \\"import os, platform; print(platform.system(), platform.release()); print(os.getcwd()); print(os.getpid())\\"")',
            'terminal(command="python -c \\"import os; print(os.access(\'.\', os.R_OK), os.access(\'.\', os.W_OK), os.access(\'.\', os.X_OK))\\"")',
            'terminal(command="python -c \\"import os; print(os.environ.get(\'PATH\', \'\').split(os.pathsep)[:5])\\"")',
            'process(action="list")',
            'read_file(path="<expected-artifact-path>")',
        ),
        "emh-update-recovery": (
            "python3 skills/emh-release-intelligence/scripts/source_status.py --offline",
            "hermes --version",
            "hermes version",
            "hermes update --help",
            "hermes status --all",
            "hermes logs list",
            "hermes gateway status",
            "hermes config check",
            'read_file(path="<redacted-update-log-path>", offset=1, limit=200)',
        ),
    }

    for name, commands in expected.items():
        assert read_only_allowlist(name) == commands
        approval_section = section(skill_body(name), "Safety and approval boundaries")
        assert "explicit approval" in approval_section
        assert "verified backup" in approval_section
        assert "rollback" in approval_section
        assert "Never silently" in approval_section


def test_v02_escalation_packets_add_domain_specific_classification():
    expected = {
        "emh-interface-diagnostics": "Layer comparison",
        "emh-tool-runtime-diagnostics": "Pipeline classification",
        "emh-environment-diagnostics": "Cross-platform matrix",
        "emh-update-recovery": "Recovery readiness",
    }
    for name, field in expected.items():
        escalation = section(skill_body(name), "Escalation packet requirements")
        assert f"**{field}:**" in escalation


def test_v02_references_route_new_skills_and_pin_bounded_official_sources():
    subsystem_map = (
        SKILLS_ROOT / "emh-triage/references/subsystem-map.md"
    ).read_text(encoding="utf-8")
    source_index = (
        SKILLS_ROOT / "emh-triage/references/official-source-index.md"
    ).read_text(encoding="utf-8")

    assert all(name in subsystem_map for name in V02_SKILLS)
    urls = (
        "https://hermes-agent.nousresearch.com/docs/user-guide/cli",
        "https://hermes-agent.nousresearch.com/docs/user-guide/tui",
        "https://hermes-agent.nousresearch.com/docs/user-guide/desktop",
        "https://hermes-agent.nousresearch.com/docs/user-guide/features/tools",
        "https://hermes-agent.nousresearch.com/docs/developer-guide/tools-runtime",
        "https://hermes-agent.nousresearch.com/docs/user-guide/configuration",
        "https://hermes-agent.nousresearch.com/docs/user-guide/security",
        "https://hermes-agent.nousresearch.com/docs/getting-started/updating",
        "https://hermes-agent.nousresearch.com/docs/user-guide/windows-native",
    )
    assert all(url in source_index for url in urls)
