import hashlib
import importlib.util
import ipaddress
import os
import re
import stat
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

import pytest
import yaml


ROOT = Path(__file__).parents[1]
REVIEWED_MEDIA_RELATIVE_PATH = "docs/assets/emh-concept-art.png"
REVIEWED_MEDIA_SHA256 = "c579fe9722afec739f88efc8c7bd4d40e5af57e78840c80906e111dd352a239c"
INFOGRAAPHIC_MEDIA_RELATIVE_PATH = "docs/assets/emh-infographic.png"
INFOGRAAPHIC_MEDIA_SHA256 = "92daef32225c422c929ea0877ddad7146b492120c9b33a3a1b2ef69916cc497e"
# Reviewed-media registry: exact path, pinned SHA-256, expected PNG geometry.
REVIEWED_MEDIA = {
    REVIEWED_MEDIA_RELATIVE_PATH: {"sha256": REVIEWED_MEDIA_SHA256, "width": 1254, "height": 1254},
    INFOGRAAPHIC_MEDIA_RELATIVE_PATH: {"sha256": INFOGRAAPHIC_MEDIA_SHA256, "width": 1254, "height": 2508},
}
SANITIZED_MEDIA_SOURCE = ROOT / REVIEWED_MEDIA_RELATIVE_PATH
TRIAGE_SCRIPT = ROOT / "skills/emh-triage/scripts/collect_vitals.py"
RELEASE_SCRIPT = ROOT / "skills/emh-release-intelligence/scripts/source_status.py"
SKILL_FILES = sorted((ROOT / "skills").glob("*/SKILL.md"))
IGNORED_DIRS = {".git", ".pytest_cache", "__pycache__", ".mypy_cache", ".ruff_cache"}
ALLOWED_PRIVATE_ROOT = Path("docs/plans")
MUTATION_WORDS = {
    "install",
    "update",
    "restart",
    "delete",
    "remove",
    "prune",
    "repair",
    "fetch",
    "reset",
    "checkout",
    "stash",
    "clean",
    "push",
}
PUBLIC_COMMANDS = {
    ("hermes", "--version"),
    ("hermes", "memory", "status"),
    ("hermes", "kanban", "stats"),
    ("hermes", "plugins", "list"),
    ("hermes", "gateway", "status"),
    ("hermes", "profile", "list"),
    ("hermes", "sessions", "stats"),
    ("hermes", "skills", "list"),
    ("hermes", "tools", "list"),
}
EXPECTED_SKILL_VERSIONS = {
    "emh-triage": "0.1.0",
    "emh-memory-diagnostics": "0.2.0",
    "emh-kanban-diagnostics": "0.2.0",
    "emh-plugin-diagnostics": "0.2.0",
    "emh-gateway-diagnostics": "0.2.0",
    "emh-provider-diagnostics": "0.2.0",
    "emh-profile-session-skill-diagnostics": "0.2.0",
    "emh-release-intelligence": "0.1.0",
    "emh-interface-diagnostics": "0.2.0",
    "emh-tool-runtime-diagnostics": "0.2.0",
    "emh-environment-diagnostics": "0.2.0",
    "emh-update-recovery": "0.2.0",
    "emh-nightly-self-check": "0.2.0",
    "emh-orientation": "0.2.0",
    "emh-rescue-media": "0.2.0",
}


_CREDENTIAL_SHAPE_PATTERN = re.compile(
    r"(?i)(?<![A-Za-z0-9])(?:"
    r"sk-(?:proj-|ant-)?[A-Za-z0-9_-]{16,}|"
    r"github_pat_[A-Za-z0-9_]{16,}|"
    r"gh[pousr]_[A-Za-z0-9_]{16,}|"
    r"(?:AKIA|ASIA)[A-Z0-9]{16,}|"
    r"AIza[A-Za-z0-9_-]{16,}|"
    r"hf_[A-Za-z0-9]{16,}|"
    r"xox[a-z]+-[A-Za-z0-9-]{16,}|"
    r"xai-[A-Za-z0-9_-]{16,}|"
    r"[0-9]{8,10}:[A-Za-z0-9_-]{30,}"
    r")(?![A-Za-z0-9])"
)
_JWT_PATTERN = re.compile(r"\beyJ[A-Za-z0-9_-]{4,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b")
_PRIVATE_KEY_PATTERN = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")
_SENSITIVE_ASSIGNMENT_PATTERN = re.compile(
    r'''(?P<key>"[^"\r\n]+"|'[^'\r\n]+'|[A-Za-z][A-Za-z0-9_-]*)'''
    r'''\s*[:=]\s*'''
    r'''(?P<value>"(?:\\.|[^"\\\r\n])*"|'(?:\\.|[^'\\\r\n])*'|[^\s,;}"']+)'''
)
_SAFE_ATOMIC_ASSIGNMENT_VALUES = frozenset(
    {
        "[REDACTED]",
        "[REDACTED_CREDENTIAL]",
        "[REDACTED_IDENTIFIER]",
        "[REDACTED_URL]",
        "[REDACTED_JWT]",
        "[REDACTED_PHONE]",
        "[REDACTED_PRIVATE_URL]",
        "***",
    }
)
_SAFE_PATH_ASSIGNMENT_VALUE = re.compile(
    r"^\[(?:HOME|REDACTED_PATH|REDACTED_RELATIVE_PATH)\](?:[\\/].*)?$"
)
_URL_PATTERN = re.compile(r"(?i)(?<![A-Za-z0-9])https?://[^\s<>\"`]+")
_AUDITED_MEDIA_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_AUDITED_MEDIA_IHDR = bytes((8, 2, 0, 0, 0))
_MEMORY_MARKERS = (
    "BEGIN RAW " + "LOG",
    "INCIDENT " + "TRANSCRIPT",
    "PRIVATE_" + "MEMORY",
    "CHAT_" + "ID",
)
_MEMORY_MARKER_PATTERN = re.compile("|".join(re.escape(marker) for marker in _MEMORY_MARKERS))
_PRIVATE_USER_PATH = "/Users/" + "jonathan"
_SENSITIVE_KEY_MARKERS = (
    "apikey",
    "accesskey",
    "accesstoken",
    "refreshtoken",
    "authorization",
    "bearer",
    "password",
    "passwd",
    "secret",
    "cookie",
    "oauth",
    "token",
)


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


def decode_bytes(data: bytes) -> str:
    """Decode repository content strictly; malformed UTF-8 is never silently skipped."""
    return data.decode("utf-8")


def _normalise_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower().strip("\\\"'"))


def _is_sensitive_key(value: str) -> bool:
    normalised = _normalise_key(value)
    return any(marker in normalised for marker in _SENSITIVE_KEY_MARKERS)


def _is_sensitive_assignment(match: re.Match[str]) -> bool:
    value = match.group("value")
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    if value.startswith(("re.", "Path(", "urlsplit(", "tuple(")):
        return False
    if value in _SAFE_ATOMIC_ASSIGNMENT_VALUES or _SAFE_PATH_ASSIGNMENT_VALUE.fullmatch(value):
        return False
    return _is_sensitive_key(match.group("key"))


def _is_official_url(url: str) -> bool:
    try:
        parsed = urlsplit(url)
        if parsed.scheme.lower() != "https" or parsed.username or parsed.password:
            return False
        if parsed.query or parsed.fragment or parsed.port is not None:
            return False
        host = (parsed.hostname or "").lower()
        path = parsed.path.rstrip("/")
        return (
            host == "hermes-agent.nousresearch.com"
            and (path == "/docs" or path.startswith("/docs/"))
        ) or (
            host == "github.com"
            and (path == "/NousResearch/hermes-agent" or path.startswith("/NousResearch/hermes-agent/"))
        ) or (
            host == "api.github.com"
            and (path == "/repos/NousResearch/hermes-agent" or path.startswith("/repos/NousResearch/hermes-agent/"))
        )
    except ValueError:
        return False


def _finding(relative_path: str, line_number: int, category: str, detail: str) -> str:
    return f"{relative_path}:{line_number}: {category}: {detail}"


def scan_text(relative_path: str, text: str) -> list[str]:
    """Return deterministic public-safety findings for one decoded text artifact."""
    findings: list[str] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if _PRIVATE_USER_PATH in line and not Path(relative_path).is_relative_to(ALLOWED_PRIVATE_ROOT):
            findings.append(_finding(relative_path, line_number, "hardcoded local path", "[REDACTED_PATH]"))

        for match in _CREDENTIAL_SHAPE_PATTERN.finditer(line):
            findings.append(_finding(relative_path, line_number, "credential", "[REDACTED_CREDENTIAL]"))

        for match in _JWT_PATTERN.finditer(line):
            findings.append(_finding(relative_path, line_number, "credential", "[REDACTED_CREDENTIAL]"))

        for match in _PRIVATE_KEY_PATTERN.finditer(line):
            findings.append(_finding(relative_path, line_number, "private key", "header detected"))

        for match in _SENSITIVE_ASSIGNMENT_PATTERN.finditer(line):
            if _is_sensitive_assignment(match):
                findings.append(_finding(relative_path, line_number, "credential assignment", "assignment detected"))

        for match in _MEMORY_MARKER_PATTERN.finditer(line):
            findings.append(_finding(relative_path, line_number, "private memory/log marker", "marker detected"))

        for match in _URL_PATTERN.finditer(line):
            url = match.group(0).rstrip(".,;!?)]}")
            if url and not _is_official_url(url):
                findings.append(_finding(relative_path, line_number, "unsafe URL", "[REDACTED_URL]"))

        if "\x00" in line or any(ord(char) < 8 for char in line):
            findings.append(_finding(relative_path, line_number, "binary content", "control byte"))
    return findings


def _is_exact_audited_media(relative_path: str, data: bytes) -> bool:
    """Return true only for a reviewed PNG at its exact repository path."""
    contract = REVIEWED_MEDIA.get(relative_path)
    if contract is None:
        return False
    if hashlib.sha256(data).hexdigest() != contract["sha256"]:
        return False
    if len(data) < 33 or data[:8] != _AUDITED_MEDIA_SIGNATURE:
        return False
    if int.from_bytes(data[8:12], "big") != 13 or data[12:16] != b"IHDR":
        return False
    if int.from_bytes(data[16:20], "big") != contract["width"]:
        return False
    if int.from_bytes(data[20:24], "big") != contract["height"]:
        return False
    return data[24:29] == _AUDITED_MEDIA_IHDR


def scan_bytes(relative_path: str, data: bytes) -> list[str]:
    try:
        text = decode_bytes(data)
    except UnicodeDecodeError:
        return [_finding(relative_path, 1, "undecodable UTF-8", "strict decode failed")]
    if b"\x00" in data:
        return [_finding(relative_path, 1, "binary content", "NUL byte")]
    return scan_text(relative_path, text)


def scan_repository_bytes(relative_path: str, data: bytes) -> list[str]:
    """Scan one repository artifact, allowing only the exact audited media contract."""
    if _is_exact_audited_media(relative_path, data):
        return []
    return scan_bytes(relative_path, data)


def scan_repository() -> list[str]:
    findings: list[str] = []
    for path in repo_files():
        relative = path.relative_to(ROOT).as_posix()
        try:
            data = path.read_bytes()
        except OSError as exc:
            findings.append(_finding(relative, 1, "unreadable artifact", type(exc).__name__))
            continue
        findings.extend(scan_repository_bytes(relative, data))
    return sorted(findings)


def test_scan_text_does_not_allow_prior_or_same_line_fixture_markers_to_bypass():
    key = "api" + "_key"
    fixture_value = "sk" + "-" + ("A" * 20)
    prior_line = "# " + "test"
    same_line = "# " + "fake"

    for text in (f"{prior_line}\n{key}={fixture_value}", f"{same_line} {key}={fixture_value}"):
        findings = scan_text("fixture.py", text)
        assert any("credential" in finding for finding in findings), findings


@pytest.mark.parametrize(
    "credential",
    [
        "sk" + "-" + ("A" * 20),
        "sk" + "-" + "proj-" + ("A" * 20),
        "sk" + "-" + "ant-" + ("A" * 20),
        "gh" + "p_" + ("A" * 20),
        "AKIA" + ("A" * 20),
        "ASIA" + ("A" * 20),
        "AIza" + ("A" * 20),
        "hf" + "_" + ("A" * 20),
        "xox" + "b-" + ("A" * 20),
        "xox" + "b-" + ("1" * 12) + "-" + ("2" * 12) + "-" + ("A" * 20),
        "xai" + "-" + ("A" * 20),
        "123456789" + ":" + ("A" * 30),
        "eyJ" + ("A" * 12) + "." + ("B" * 12) + "." + ("C" * 12),
    ],
)
def test_scan_text_detects_each_production_credential_shape(credential):
    findings = scan_text("fixture.txt", "value=" + credential)
    assert any("credential" in finding for finding in findings), findings


def test_scan_text_detects_fine_grained_github_token_constructed_at_runtime():
    credential = "github" + "_pat_" + ("A" * 24)

    findings = scan_text("fixture.txt", "value=" + credential)

    assert any("fixture.txt:1: credential:" in finding for finding in findings), findings
    assert all(credential not in finding for finding in findings)


def test_scan_text_findings_redact_all_matched_sensitive_content():
    credential = "github" + "_pat_" + ("B" * 24)
    assignment = "API" + "_KEY=" + "assignment-secret-value"
    url = "https" + "://evil.example.test/private?" + "token" + "=url-secret-value"
    private_path = "/Users/" + "jonathan" + "/private/notes.txt"
    private_key_header = "-----BEGIN " + "RSA PRIVATE KEY-----"
    memory_marker = "PRIVATE_" + "MEMORY"
    cases = [
        ("credential.txt", "value=" + credential, "credential", (credential,)),
        ("assignment.env", assignment, "credential assignment", (assignment, "API_KEY", "assignment-secret-value")),
        ("url.txt", url, "unsafe URL", (url, "evil.example.test", "url-secret-value")),
        ("path.txt", private_path, "hardcoded local path", (private_path, "jonathan")),
        ("key.pem", private_key_header, "private key", (private_key_header, "RSA PRIVATE KEY")),
        ("memory.log", memory_marker, "private memory/log marker", (memory_marker,)),
    ]

    for relative_path, text, category, sensitive_fragments in cases:
        findings = scan_text(relative_path, text)
        matching = [finding for finding in findings if category in finding]
        assert matching, (relative_path, findings)
        for finding in matching:
            assert f"{relative_path}:1: {category}:" in finding
            assert all(fragment not in finding for fragment in sensitive_fragments)


def test_scan_text_detects_sensitive_assignments_across_key_styles():
    keys = [
        "vendor" + "_" + "API" + "_" + "KEY",
        "access" + "-" + "token",
        "client" + "Secret",
        "session" + "Password",
        "browser" + "Cookie",
        "http" + "Authorization",
        "OAuth" + "Token",
    ]
    text = "\n".join(f"{key} = credential-{index:02d}" for index, key in enumerate(keys))
    findings = scan_text("fixture.env", text)
    assert len([finding for finding in findings if "credential" in finding]) >= len(keys)


def test_scan_text_does_not_exempt_bracketed_or_mapping_sensitive_values():
    key = "api" + "_key"
    samples = ["[generic-private-value]", "{generic-private-value}"]
    text = "\n".join(f"{key}={value}" for value in samples)

    findings = scan_text("fixture.env", text)

    assert len([finding for finding in findings if "credential assignment" in finding]) == len(samples)


def test_scan_text_allows_only_exact_safe_redaction_placeholders():
    key = "api" + "_key"
    placeholders = [
        "[REDACTED]",
        "[REDACTED_CREDENTIAL]",
        "[REDACTED_IDENTIFIER]",
        "[REDACTED_URL]",
        "[REDACTED_JWT]",
        "[REDACTED_PHONE]",
        "[REDACTED_PRIVATE_URL]",
        "[REDACTED_PATH]/safe-name",
        "[REDACTED_RELATIVE_PATH]/safe-name",
        "[HOME]/.hermes/hermes-agent",
        "***",
    ]
    text = "\n".join(f"{key}={value}" for value in placeholders)

    assert scan_text("redacted-output.txt", text) == []


@pytest.mark.parametrize(
    "value",
    [
        "[REDACTED_CREDENTIAL]extra",
        "[REDACTED]/synthetic-secret",
        "[REDACTED_URL]#secret",
        "[generic-private-value]",
        "{generic-private-value}",
        '"[REDACTED_CREDENTIAL]extra"',
        '"[REDACTED]/synthetic-secret"',
        '"[REDACTED_URL]#secret"',
        '"[generic-private-value]"',
        '"{generic-private-value}"',
    ],
)
def test_scan_text_rejects_incomplete_or_generic_sensitive_placeholders(value):
    key = "api" + "_key"

    findings = scan_text("unsafe-placeholder.env", f"{key}={value}")

    matching = [finding for finding in findings if "credential assignment" in finding]
    assert matching, (value, findings)
    assert all(value.strip('"\'') not in finding for finding in matching)


def test_scan_text_rejects_every_nonofficial_url_form_but_allows_official_families():
    official = [
        "https://" + "hermes-agent.nousresearch.com/docs",
        "https://" + "hermes-agent.nousresearch.com/docs/setup",
        "https://" + "github.com/NousResearch/hermes-agent",
        "https://" + "github.com/NousResearch/hermes-agent/releases/latest",
        "https://" + "api.github.com/repos/NousResearch/hermes-agent/releases",
    ]
    nonofficial = [
        "http://" + "example.com/public",
        "https://" + "example.org/public",
        "https://" + "service.internal/status",
        "https://" + "example.com:8443/status",
        "https://" + "user:pass@example.com/status",
        "https://" + "github.com/NousResearch/hermes-agent?" + "to" + "ken=" + "value",
        "https://" + "github.com/NousResearch/hermes-agent#fragment",
        "https://" + "127.0.0.1:8080/status",
        "https://" + "192.168.1.20/private",
        "https://" + "[fd00::1]/private",
        "https://" + "hermes-agent.nousresearch.com/docsevil",
    ]

    assert scan_text("official.md", "\n".join(official)) == []
    findings = scan_text("urls.md", "\n".join(nonofficial))
    assert len([finding for finding in findings if "URL" in finding]) == len(nonofficial)


def test_scan_text_detects_private_memory_markers_and_hardcoded_user_path():
    markers = [
        "BEGIN RAW " + "LOG",
        "INCIDENT " + "TRANSCRIPT",
        "PRIVATE_" + "MEMORY",
        "CHAT_" + "ID",
    ]
    text = "\n".join(markers) + "\n" + "/Users/" + "jonathan/.hermes/private"
    findings = scan_text("copied.log", text)
    assert len([finding for finding in findings if "memory" in finding]) == len(markers)
    assert any("local path" in finding for finding in findings)


def test_scan_text_detects_private_key_headers_without_fixture_exceptions():
    header = "-----BEGIN " + "RSA PRIVATE KEY-----"
    findings = scan_text("key.pem", "# " + "fake\n" + header)
    assert any("private key" in finding for finding in findings), findings


def test_scan_bytes_fails_closed_for_invalid_utf8_and_binary_content():
    with pytest.raises(UnicodeDecodeError):
        decode_bytes(b"valid prefix\xff")

    invalid_findings = scan_bytes("broken.bin", b"valid prefix\xff")
    binary_findings = scan_bytes("binary.dat", b"\x00\x01\x02\x03")
    assert any("undecodable" in finding for finding in invalid_findings)
    assert any("binary" in finding for finding in binary_findings)


def test_scan_bytes_remains_strict_for_reviewed_repository_media():
    data = (ROOT / REVIEWED_MEDIA_RELATIVE_PATH).read_bytes()

    findings = scan_bytes(REVIEWED_MEDIA_RELATIVE_PATH, data)

    assert findings
    assert all("binary" in finding or "undecodable" in finding for finding in findings)


def test_reviewed_media_contract_is_self_contained():
    assert SANITIZED_MEDIA_SOURCE == ROOT / REVIEWED_MEDIA_RELATIVE_PATH


def test_scan_repository_bytes_allows_only_the_exact_reviewed_media_contract():
    data = SANITIZED_MEDIA_SOURCE.read_bytes()

    assert hashlib.sha256(data).hexdigest() == REVIEWED_MEDIA_SHA256
    assert scan_repository_bytes(REVIEWED_MEDIA_RELATIVE_PATH, data) == []


def test_infographic_media_contract_is_pinned_and_geometry_exact():
    path = ROOT / INFOGRAAPHIC_MEDIA_RELATIVE_PATH
    data = path.read_bytes()

    assert hashlib.sha256(data).hexdigest() == INFOGRAAPHIC_MEDIA_SHA256
    assert data[:8] == _AUDITED_MEDIA_SIGNATURE
    assert int.from_bytes(data[16:20], "big") == 1254
    assert int.from_bytes(data[20:24], "big") == 2508
    assert data[24:29] == _AUDITED_MEDIA_IHDR
    assert scan_repository_bytes(INFOGRAAPHIC_MEDIA_RELATIVE_PATH, data) == []


def test_scan_repository_bytes_rejects_one_bit_mutation_of_reviewed_media():
    data = bytearray(SANITIZED_MEDIA_SOURCE.read_bytes())
    data[-1] ^= 1

    findings = scan_repository_bytes(REVIEWED_MEDIA_RELATIVE_PATH, bytes(data))

    assert findings
    assert all("binary" in finding or "undecodable" in finding for finding in findings)
    assert all(bytes(data).hex() not in finding for finding in findings)


def test_scan_repository_bytes_rejects_reviewed_media_at_an_unapproved_path():
    findings = scan_repository_bytes(
        "docs/assets/copy.png", SANITIZED_MEDIA_SOURCE.read_bytes()
    )

    assert findings
    assert all("binary" in finding or "undecodable" in finding for finding in findings)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda data: data[:32],
        lambda data: data[:16] + (1255).to_bytes(4, "big") + data[20:],
    ],
)
def test_scan_repository_bytes_rejects_malformed_or_wrong_metadata_reviewed_media(mutate):
    data = mutate(SANITIZED_MEDIA_SOURCE.read_bytes())

    findings = scan_repository_bytes(REVIEWED_MEDIA_RELATIVE_PATH, data)

    assert findings
    assert all("binary" in finding or "undecodable" in finding for finding in findings)


def test_readme_references_only_the_reviewed_media_with_safe_caption():
    readme = read_text(ROOT / "README.md")
    alt_text = (
        "EMH concept artwork showing a clinical diagnostic hologram beside "
        "Emergency Medical Hermes branding and feature callouts."
    )

    assert readme.count(REVIEWED_MEDIA_RELATIVE_PATH) == 1
    assert f"![{alt_text}]({REVIEWED_MEDIA_RELATIVE_PATH})" in readme
    assert "fan-inspired, unofficial, and unaffiliated" in readme
    assert "emh-readme-sanitized.png" not in readme
    assert "C:" not in readme
    assert "/Users/" not in readme



def test_scan_text_allows_harmless_prose_versions_hashes_and_official_urls():
    text = (
        "This test describes a fictional redaction policy.\n"
        "Hermes Agent v0.20.0 commit 0123456789abcdef0123456789abcdef01234567\n"
        "https://" + "hermes-agent.nousresearch.com/docs"
    )
    assert scan_text("harmless.md", text) == []


def repo_files():
    for directory, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = sorted(name for name in dirnames if name not in IGNORED_DIRS)
        for filename in sorted(filenames):
            yield Path(directory) / filename


def read_text(path: Path) -> str:
    return decode_bytes(path.read_bytes())


def load_script(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_inventory_includes_untracked_source_files_and_required_payload():
    paths = {path.relative_to(ROOT).as_posix() for path in repo_files()}
    assert "tests/test_public_safety.py" in paths
    assert "skills/emh-triage/SKILL.md" in paths
    assert REVIEWED_MEDIA_RELATIVE_PATH in paths
    assert all(not path.startswith(".git/") for path in paths)
    assert all("__pycache__" not in path for path in paths)


def test_reviewed_media_has_exact_bytes_mode_and_png_geometry():
    path = ROOT / REVIEWED_MEDIA_RELATIVE_PATH
    data = path.read_bytes()

    assert hashlib.sha256(data).hexdigest() == REVIEWED_MEDIA_SHA256
    assert stat.S_IMODE(path.stat().st_mode) == 0o644
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    assert int.from_bytes(data[16:20], "big") == 1254
    assert int.from_bytes(data[20:24], "big") == 1254
    assert data[24:29] == bytes((8, 2, 0, 0, 0))


def test_all_skill_frontmatter_is_real_yaml_and_public_safe():
    assert {path.parent.name for path in SKILL_FILES} == set(EXPECTED_SKILL_VERSIONS)
    for path in SKILL_FILES:
        content = read_text(path)
        assert content.startswith("---\n")
        _, frontmatter, body = content.split("---", 2)
        metadata = yaml.safe_load(frontmatter)
        assert isinstance(metadata, dict)
        assert metadata["name"] == path.parent.name
        assert metadata["version"] == EXPECTED_SKILL_VERSIONS[path.parent.name]
        assert metadata["author"] == "Jonathan Rivera"
        assert metadata["license"] == "UNLICENSED"
        assert metadata["platforms"] == ["linux", "macos", "windows"]
        assert metadata["description"].startswith("Use when ")
        assert metadata["description"].strip() == metadata["description"]
        assert body.strip()
        sections = (
            ("## Workflow", "## Safety boundaries", "## Pitfalls", "## Verification")
            if metadata["version"] == "0.1.0"
            else (
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
        )
        for section in sections:
            assert _has_markdown_heading(body, section)


def test_repository_inventory_rejects_secrets_private_paths_and_copied_private_material():
    assert scan_repository() == []


def test_repository_has_no_bundled_runtime_or_remote_artifact_files():
    forbidden_names = {
        ".env",
        "config.yaml",
        "config.yml",
        "credentials.json",
        "auth.json",
        "cookies.txt",
        "license",
        "copying",
        "cron",
        "mcp",
        "telemetry",
        "uploader",
        "remote-metadata.json",
        "provider-config.yaml",
        "plugin.py",
        "plugin.json",
        "plugin.yaml",
        "plugin.toml",
    }
    for path in repo_files():
        relative_parts = {part.lower() for part in path.relative_to(ROOT).parts}
        assert not relative_parts.intersection(forbidden_names), path
        assert path.name.lower() not in forbidden_names, path


def test_diagnostic_scripts_compile_and_expose_only_read_only_command_vectors():
    collect = load_script(TRIAGE_SCRIPT, "collect_vitals_public_safety")
    release = load_script(RELEASE_SCRIPT, "source_status_public_safety")
    assert {tuple(command) for command in collect.COMMANDS.values()} == PUBLIC_COMMANDS
    assert all(not set(command).intersection(MUTATION_WORDS) for command in collect.COMMANDS.values())

    seen = []

    def runner(args, **kwargs):
        seen.append(tuple(args))
        if tuple(args) == ("hermes", "--version"):
            return subprocess.CompletedProcess(args, 0, stdout="Hermes Agent v0.20.0\n", stderr="")
        return subprocess.CompletedProcess(args, 0, stdout="ok\n", stderr="")

    collect.collect_vitals(subsystems=list(collect.COMMANDS), runner=runner)
    assert set(seen) == PUBLIC_COMMANDS
    assert release.VERSION_COMMAND == ("hermes", "version")
    assert not set(release.VERSION_COMMAND).intersection(MUTATION_WORDS)

    compile_targets = (TRIAGE_SCRIPT, RELEASE_SCRIPT)
    for target in compile_targets:
        subprocess.run(
            [sys.executable, "-m", "py_compile", str(target)],
            check=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        assert stat.S_IMODE(target.stat().st_mode) == 0o755
