import importlib.util
import json
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "skills/emh-release-intelligence/scripts/source_status.py"


def load_module():
    spec = importlib.util.spec_from_file_location("source_status", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_parse_hermes_version_output_extracts_install_and_update_status():
    module = load_module()
    output = """Hermes Agent v0.20.0 (2026.8.3) · upstream b3aa561f
Install directory: /fictional Hermes installs/hermes-agent
Install method: git
Python: 3.11.15
OpenAI SDK: 2.24.0
Update available: 247 commits behind — run 'hermes update'
"""

    parsed = module.parse_hermes_version(output)

    assert parsed == {
        "version": "0.20.0",
        "install_directory": "[REDACTED_PATH]/hermes-agent",
        "install_method": "git",
        "update_status": "247 commits behind",
        "update_available": True,
    }


def test_source_status_redacts_windows_home_paths_without_leaking_the_drive():
    module = load_module()

    parsed = module.parse_hermes_version(
        "Hermes Agent v2026.8.3\n"
        r"Install directory: C:\Users\Example\.hermes\hermes-agent" "\n"
        "Install method: pipx\n"
    )

    assert parsed["install_directory"] == r"[HOME]\.hermes\hermes-agent"
    assert "Example" not in json.dumps(parsed)
    assert r"C:\Users" not in json.dumps(parsed)


def test_source_status_redaction_preserves_versions_and_redacts_phone_numbers():
    module = load_module()

    redacted = module.redact("Hermes v2026.8.3; phone +1 (415) 555-0199")

    assert "v2026.8.3" in redacted
    assert "+1 (415) 555-0199" not in redacted
    assert "[REDACTED_PHONE]" in redacted


def test_summarize_git_reports_commit_dirty_and_count_without_filenames():
    module = load_module()
    calls = []
    porcelain = b" M private.env\x00?? secrets.txt\x00"

    def runner(args, **kwargs):
        calls.append((args, kwargs))
        if args[3] == "rev-parse":
            return subprocess.CompletedProcess(args, 0, stdout="abc123def456\n", stderr="")
        return subprocess.CompletedProcess(args, 0, stdout=porcelain, stderr=b"")

    result = module.summarize_git("/private/install", runner=runner)

    assert result == {
        "status": "success",
        "commit": "abc123def456",
        "clean": False,
        "change_count": 2,
    }
    assert [call[0] for call in calls] == [
        ["git", "-C", "/private/install", "rev-parse", "HEAD"],
        ["git", "-C", "/private/install", "status", "--porcelain=v1", "-z"],
    ]
    assert all("private.env" not in json.dumps(result) for _ in [0])
    assert all(call[1]["shell"] is False for call in calls)


def test_parse_release_payload_returns_versioned_official_metadata():
    module = load_module()

    parsed = module.parse_release_payload(
        {
            "tag_name": "v2026.8.3",
            "name": "2026.8.3",
            "html_url": "https://github.com/NousResearch/hermes-agent/releases/tag/v2026.8.3",
            "published_at": "2026-08-03T16:57:52Z",
        }
    )

    assert parsed == {
        "tag": "v2026.8.3",
        "name": "2026.8.3",
        "html_url": "https://github.com/NousResearch/hermes-agent/releases/tag/v2026.8.3",
        "published_at": "2026-08-03T16:57:52Z",
        "version": "2026.8.3",
    }


@pytest.mark.parametrize(
    "html_url",
    [
        "https" + "://github.com/NousResearch/hermes-agent/releases/tag/v2026.8.3?token=secret",
        "https" + "://github.com/NousResearch/hermes-agent/releases/tag/v2026.8.3#secret",
        "https" + "://user:pass@github.com/NousResearch/hermes-agent/releases/tag/v2026.8.3",
        "https" + "://github.com:443/NousResearch/hermes-agent/releases/tag/v2026.8.3",
        "http" + "://github.com/NousResearch/hermes-agent/releases/tag/v2026.8.3",
        "https" + "://evil.example/NousResearch/hermes-agent/releases/tag/v2026.8.3",
        "https" + "://github.com/NousResearch/hermes-agent",
        "https" + "://github.com/NousResearch/hermes-agent/issues/1",
        "https" + "://github.com/NousResearch/hermes-agent/tree/main",
    ],
)
def test_parse_release_payload_rejects_unsafe_or_non_release_urls(html_url):
    module = load_module()
    payload = {
        "tag_name": "v2026.8.3",
        "name": "2026.8.3",
        "html_url": html_url,
        "published_at": "2026-08-03T16:57:52Z",
    }

    with pytest.raises(ValueError):
        module.parse_release_payload(payload)


@pytest.mark.parametrize("tag", ["v2026.8", "release-2026.8.3", "v2026.8.3/secret", "v2026.8.3?secret"])
def test_parse_release_payload_rejects_malformed_tags(tag):
    module = load_module()
    payload = {
        "tag_name": tag,
        "name": "2026.8.3",
        "html_url": "https://github.com/NousResearch/hermes-agent/releases/tag/v2026.8.3",
        "published_at": "2026-08-03T16:57:52Z",
    }

    with pytest.raises(ValueError):
        module.parse_release_payload(payload)


@pytest.mark.parametrize(
    "tag",
    ["v01.2.3", "v1.02.3", "v1.2.03", "01.2.3", "1.02.3", "1.2.03"],
)
def test_parse_release_payload_rejects_semver_tags_with_leading_zeroes(tag):
    module = load_module()
    payload = {
        "tag_name": tag,
        "name": tag,
        "html_url": f"https://github.com/NousResearch/hermes-agent/releases/tag/{tag}",
        "published_at": "2026-08-03T16:57:52Z",
    }

    with pytest.raises(ValueError):
        module.parse_release_payload(payload)


@pytest.mark.parametrize(
    "html_url",
    [
        "https://github.com/NousResearch/hermes-agent/releases/foo",
        "https://github.com/NousResearch/hermes-agent/releases/latest",
        "https://github.com/NousResearch/hermes-agent/releases/tag/evil",
        "https://github.com/NousResearch/hermes-agent/releases/tag/v2026.8.3/extra",
        "https://github.com/NousResearch/hermes-agent/releases/tag/v2026.8.3%2Fextra",
        "https://github.com/NousResearch/hermes-agent/releases/tag/v2026.8.3%252Fextra",
        "https://github.com/NousResearch/hermes-agent/releases/tag/v2026.8.4",
    ],
)
def test_parse_release_payload_rejects_noncanonical_or_mismatched_release_urls(html_url):
    module = load_module()
    payload = {
        "tag_name": "v2026.8.3",
        "name": "2026.8.3",
        "html_url": html_url,
        "published_at": "2026-08-03T16:57:52Z",
    }

    with pytest.raises(ValueError):
        module.parse_release_payload(payload)


def test_parse_release_payload_accepts_unprefixed_strict_semver_tag_with_exact_url():
    module = load_module()
    tag = "0.20.0"

    parsed = module.parse_release_payload(
        {
            "tag_name": tag,
            "name": tag,
            "html_url": f"https://github.com/NousResearch/hermes-agent/releases/tag/{tag}",
            "published_at": "2026-08-03T16:57:52Z",
        }
    )

    assert parsed["tag"] == tag
    assert parsed["version"] == tag


@pytest.mark.parametrize(
    "published_at",
    [
        "not-a-timestamp",
        "2026-02-30T16:57:52Z",
        "2026-08-03T25:57:52Z",
        "2026-08-03T16:57:52",
        "2026-08-03T16:57:52+00:00",
        "2026-08-03T16:57:52-04:00",
        "2026-08-03T16:57:52z",
    ],
)
def test_parse_release_payload_rejects_invalid_or_non_utc_published_at(published_at):
    module = load_module()
    payload = {
        "tag_name": "v2026.8.3",
        "name": "2026.8.3",
        "html_url": "https://github.com/NousResearch/hermes-agent/releases/tag/v2026.8.3",
        "published_at": published_at,
    }

    with pytest.raises(ValueError):
        module.parse_release_payload(payload)


@pytest.mark.parametrize("published_at", ["2026-08-03T16:57:52Z", "2026-08-03T16:57:52.123456Z"])
def test_parse_release_payload_accepts_real_utc_timestamps(published_at):
    module = load_module()
    payload = {
        "tag_name": "v2026.8.3",
        "name": "2026.8.3",
        "html_url": "https://github.com/NousResearch/hermes-agent/releases/tag/v2026.8.3",
        "published_at": published_at,
    }

    parsed = module.parse_release_payload(payload)

    assert parsed["published_at"] == published_at
    assert all(isinstance(value, str) for value in parsed.values())


def test_parse_release_payload_redacts_untrusted_release_name_content():
    module = load_module()
    credential = "github" + "_pat_" + ("A" * 24)
    private_url = "https" + "://private.example.test/internal"
    private_path = "/Users/alice/private-notes"
    identifier_value = "task-secret"
    payload = {
        "tag_name": "v2026.8.3",
        "name": f"Release {credential} {private_url} {private_path} task-id={identifier_value}",
        "html_url": "https://github.com/NousResearch/hermes-agent/releases/tag/v2026.8.3",
        "published_at": "2026-08-03T16:57:52Z",
    }

    parsed = module.parse_release_payload(payload)

    assert credential not in parsed["name"]
    assert private_url not in parsed["name"]
    assert private_path not in parsed["name"]
    assert identifier_value not in parsed["name"]
    assert "[REDACTED_CREDENTIAL]" in parsed["name"]
    assert "[REDACTED_URL]" in parsed["name"]
    assert "[HOME]" in parsed["name"]
    assert "[REDACTED_IDENTIFIER]" in parsed["name"]


class FakeResponse:
    status = 200

    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, limit):
        assert limit == 64 * 1024 + 1
        return self.body


def test_fetch_latest_release_uses_only_official_endpoint_and_bounded_request():
    module = load_module()
    calls = []
    body = json.dumps(
        {
            "tag_name": "v2026.8.3",
            "name": "2026.8.3",
            "html_url": "https://github.com/NousResearch/hermes-agent/releases/tag/v2026.8.3",
            "published_at": "2026-08-03T16:57:52Z",
        }
    ).encode()

    def urlopen(request, timeout):
        calls.append((request, timeout))
        return FakeResponse(body)

    result = module.fetch_latest_release(urlopen=urlopen)

    assert result["status"] == "success"
    assert calls[0][0].full_url == module.RELEASE_API_URL
    assert calls[0][0].get_header("User-agent") == module.USER_AGENT
    assert calls[0][1] == 5.0


def test_fetch_latest_release_degrades_for_offline_http_malformed_and_timeout():
    module = load_module()

    # fake test fixture: representative offline endpoint only
    def offline(request, timeout):
        # fake test fixture value is intentionally synthetic
        raise module.urllib.error.URLError("private token at " + "http" + "://" + "127.0.0.1:9")

    def http_error(request, timeout):
        raise module.urllib.error.HTTPError(module.RELEASE_API_URL, 503, "private path", {}, None)

    def malformed(request, timeout):
        return FakeResponse(b"not-json")

    def timed_out(request, timeout):
        raise TimeoutError("secret at /private/path")

    assert module.fetch_latest_release(urlopen=offline)["status"] == "unavailable"
    assert module.fetch_latest_release(urlopen=http_error)["status"] == "failed"
    assert module.fetch_latest_release(urlopen=malformed)["status"] == "failed"
    assert module.fetch_latest_release(urlopen=timed_out)["status"] == "timed_out"

    serialized = json.dumps(
        [
            module.fetch_latest_release(urlopen=offline),
            module.fetch_latest_release(urlopen=http_error),
            module.fetch_latest_release(urlopen=malformed),
            module.fetch_latest_release(urlopen=timed_out),
        ]
    )
    assert "127.0.0.1" not in serialized
    assert "/private/path" not in serialized
    assert "secret" not in serialized


def test_collect_status_offline_skips_release_fetch_and_reports_git_summary():
    module = load_module()
    calls = []
    version_output = (
        "Hermes Agent v0.20.0 (2026.8.3)\n"
        "Install directory: /tmp/hermes\n"
        "Install method: git\n"
        "Update available: 1 commit behind — run 'hermes update'\n"
    )

    def runner(args, **kwargs):
        calls.append(args)
        if args[1] == "version":
            return subprocess.CompletedProcess(args, 0, stdout=version_output, stderr="")
        if args[3] == "rev-parse":
            return subprocess.CompletedProcess(args, 0, stdout="abc1234\n", stderr="")
        return subprocess.CompletedProcess(args, 0, stdout=b"", stderr=b"")

    def release_fetcher(**kwargs):
        raise AssertionError("offline mode must not query releases")

    result = module.collect_status(
        offline=True,
        runner=runner,
        release_fetcher=release_fetcher,
    )

    assert result["latest_release"] == {"status": "offline"}
    assert result["current"] == {
        "version": "0.20.0",
        "install_directory": "[REDACTED_PATH]/hermes",
        "install_method": "git",
        "update_status": "1 commit behind",
        "update_available": True,
    }
    assert result["git"] == {
        "status": "success",
        "commit": "abc1234",
        "clean": True,
        "change_count": 0,
    }
    assert calls[0] == ["hermes", "version"]


def test_collect_status_probes_git_with_raw_path_but_returns_only_redacted_summary():
    module = load_module()
    raw_path = "/Users/example/.hermes/hermes-agent"
    version_output = (
        "Hermes Agent v0.20.0 (2026.8.3)\n"
        f"Install directory: {raw_path}\n"
        "Install method: git\n"
    )
    calls = []

    def runner(args, **kwargs):
        calls.append(args)
        if args == ["hermes", "version"]:
            return subprocess.CompletedProcess(args, 0, stdout=version_output, stderr="")
        if args == ["git", "-C", raw_path, "rev-parse", "HEAD"]:
            return subprocess.CompletedProcess(args, 0, stdout="abc1234\n", stderr="")
        if args == ["git", "-C", raw_path, "status", "--porcelain=v1", "-z"]:
            return subprocess.CompletedProcess(args, 0, stdout=b"", stderr=b"")
        raise AssertionError("unexpected command")

    result = module.collect_status(offline=True, runner=runner)
    serialized = json.dumps(result)

    assert calls[1:] == [
        ["git", "-C", raw_path, "rev-parse", "HEAD"],
        ["git", "-C", raw_path, "status", "--porcelain=v1", "-z"],
    ]
    assert result["current"]["install_directory"] == "[HOME]/.hermes/hermes-agent"
    assert raw_path not in serialized
    assert "example" not in serialized


def test_collect_status_skips_git_probes_for_non_git_installations():
    module = load_module()
    version_output = (
        "Hermes Agent v0.20.0\n"
        "Install directory: /fictional Hermes installs/hermes-agent\n"
        "Install method: pipx\n"
    )
    calls = []

    def runner(args, **kwargs):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, stdout=version_output, stderr="")

    result = module.collect_status(offline=True, runner=runner)

    assert result["status"] == "unavailable"
    assert result["git"] is None
    assert calls == [["hermes", "version"]]


def test_fetch_latest_release_degrades_safely_for_oversized_response():
    module = load_module()

    def oversized(request, timeout):
        return FakeResponse(b"x" * (module.MAX_RESPONSE_BYTES + 1))

    assert module.fetch_latest_release(urlopen=oversized) == {
        "status": "failed",
        "error": {
            "code": "response_too_large",
            "message": "Official release response exceeded the byte limit",
        },
    }


def test_source_status_main_emits_deterministic_json_with_injected_offline_runner(capsys):
    module = load_module()
    version_output = (
        "Hermes Agent v0.20.0\n"
        "Install directory: /fictional Hermes installs/hermes-agent\n"
        "Install method: pipx\n"
    )

    def runner(args, **kwargs):
        return subprocess.CompletedProcess(args, 0, stdout=version_output, stderr="")

    exit_code = module.main(["--offline"], runner=runner)

    captured = capsys.readouterr()
    assert exit_code == 1
    assert json.loads(captured.out) == {
        "current": {
            "install_directory": "[REDACTED_PATH]/hermes-agent",
            "install_method": "pipx",
            "update_available": False,
            "update_status": "unknown",
            "version": "0.20.0",
        },
        "git": None,
        "latest_release": {"status": "offline"},
        "status": "unavailable",
    }
    assert captured.err == ""


def test_source_status_public_parser_summarizes_every_private_path_class():
    module = load_module()
    cases = [
        ("/Users/Alice/project/log.txt", "[HOME]/project/log.txt"),
        ("/home/alice/project/log.txt", "[HOME]/project/log.txt"),
        (r"C:\Users\Alice\project\log.txt", r"[HOME]\project\log.txt"),
        ("C:/Users/Alice/project/log.txt", "[HOME]/project/log.txt"),
        ("~/project/log.txt", "[HOME]/project/log.txt"),
        ("$HOME/project/log.txt", "[HOME]/project/log.txt"),
        (r"%USERPROFILE%\project\log.txt", r"[HOME]\project\log.txt"),
        (r"\\server\share\Alice\project\log.txt", r"[REDACTED_PATH]\log.txt"),
        ("/etc/hermes/private.log", "[REDACTED_PATH]/private.log"),
        ("./cache/private.log", "[REDACTED_RELATIVE_PATH]/private.log"),
        ("../secrets/private.log", "[REDACTED_RELATIVE_PATH]/private.log"),
        ("relative/cache/private.log", "[REDACTED_RELATIVE_PATH]/private.log"),
        ("private.log", "[REDACTED_RELATIVE_PATH]/private.log"),
    ]
    for original, expected in cases:
        parsed = module.parse_hermes_version(
            "Hermes Agent v2026.8.3\n"
            f"Install directory: {original}\n"
            "Install method: pipx\n"
        )
        assert parsed["install_directory"] == expected
        assert original not in json.dumps(parsed).replace(expected, "")

    parsed = module.parse_hermes_version(
        "Hermes Agent v2026.8.3\n"
        'Install directory: "relative cache/private log.txt"\n'
        "Install method: pipx\n"
    )
    assert parsed["install_directory"] == '[REDACTED_RELATIVE_PATH]/private log.txt'


def test_source_status_redacts_generic_identifier_assignments_across_key_styles():
    module = load_module()
    assignments = [
        "id=bare-1",
        '"task_id": "task-2"',
        "'worker-id'='worker-3'",
        "profileId: profile-4",
        "runId=run-5",
        'ticket_id = "ticket-6"',
        "request-id='req-7'",
        "conversationId: conv-8",
        "thread_id=thread-9",
        'workspace-id="ws-10"',
    ]
    redacted = module.redact("; ".join(assignments))

    for assignment in assignments:
        value = assignment.split(":", 1)[-1].split("=", 1)[-1].strip().strip("\\\"'")
        assert value not in redacted
    assert redacted.count("[REDACTED_IDENTIFIER]") == len(assignments)


def test_source_status_redacts_prefixed_and_camel_case_credential_assignments():
    module = load_module()
    entries = [
        ("OPENAI" + "_" + "API" + "_" + "KEY", "openai" + "-" + "secret"),
        ("HERMES" + "_" + "ACCESS" + "_" + "TOKEN", "access" + " secret"),
        ("MY" + "_" + "PASSWORD", "password" + " secret"),
        ("client" + "_" + "secret", "client" + "-" + "secret"),
        ("BOT" + "_" + "TOKEN", "bot" + "-" + "secret"),
        ("api" + "Key", "api" + "-" + "secret"),
        ("refresh" + "Token", "refresh" + " secret"),
        ("coo" + "kie", "cookie" + " secret"),
        ("Author" + "ization", "Bearer" + "-" + "secret"),
    ]
    assignments = [f"{label}={value}" for label, value in entries]
    redacted = module.redact("; ".join(assignments))

    for value in [
        "openai-secret",
        "access secret",
        "password secret",
        "client-secret",
        "bot-secret",
        "api-secret",
        "refresh secret",
        "cookie secret",
        "Bearer-secret",
    ]:
        assert value not in redacted
    assert redacted.count("[REDACTED]") == len(assignments)


def test_source_status_parser_and_errors_preserve_public_urls_and_versions_without_raw_paths():
    module = load_module()
    raw_path = r"\\server\\share\\Alice\\private install"
    docs_url = "https" + "://hermes-agent.nousresearch.com/docs"
    github_url = "https" + "://github.com/NousResearch/hermes-agent"
    api_url = "https" + "://api.github.com/repos/NousResearch/hermes-agent"
    output = (
        "Hermes Agent v2026.8.3 (2026.8.3)\n"
        f"Install directory: {raw_path}\n"
        "Install method: pipx\n"
        f"Docs: {docs_url}\n"
        f"Source: {github_url}\n"
        f"API: {api_url}\n"
    )
    parsed = module.parse_hermes_version(output)
    serialized = json.dumps(parsed)
    assert raw_path not in serialized
    assert "Alice" not in serialized
    assert "[REDACTED_PATH]" in serialized
    assert "2026.8.3" in serialized
    redacted_output = module.redact(output)
    for public_url in [
        "https://hermes-agent.nousresearch.com/docs",
        "https://github.com/NousResearch/hermes-agent",
        "https://api.github.com/repos/NousResearch/hermes-agent",
    ]:
        assert public_url in redacted_output


def test_source_status_collect_status_uses_raw_path_only_for_fixed_git_probes():
    module = load_module()
    raw_path = r"C:\Users\Alice\private install"
    version_output = (
        "Hermes Agent v2026.8.3\n"
        f"Install directory: {raw_path}\n"
        "Install method: git\n"
    )
    calls = []

    def runner(args, **kwargs):
        calls.append(args)
        if args == ["hermes", "version"]:
            return subprocess.CompletedProcess(args, 0, stdout=version_output, stderr="")
        if args == ["git", "-C", raw_path, "rev-parse", "HEAD"]:
            return subprocess.CompletedProcess(args, 0, stdout="abc1234\n", stderr="")
        if args == ["git", "-C", raw_path, "status", "--porcelain=v1", "-z"]:
            return subprocess.CompletedProcess(args, 0, stdout=b"", stderr=b"")
        raise AssertionError("unexpected command")

    result = module.collect_status(offline=True, runner=runner)
    assert calls[1:] == [
        ["git", "-C", raw_path, "rev-parse", "HEAD"],
        ["git", "-C", raw_path, "status", "--porcelain=v1", "-z"],
    ]
    serialized = json.dumps(result)
    assert raw_path not in serialized
    assert "Alice" not in serialized
    assert result["current"]["install_directory"] == r"[HOME]\private install"


def test_source_status_redacts_unlabeled_credentials_without_matching_safe_lookalikes():
    module = load_module()
    credentials = [
        "sk" + "-" + "proj" + "-" + ("F" * 20),
        "sk" + "-" + "ant" + "-" + ("F" * 20),
        "gh" + "p_" + ("F" * 20),
        "AKIA" + ("F" * 20),
        "AIza" + ("F" * 20),
        "hf" + "_" + ("F" * 20),
        "xox" + "b-" + ("F" * 20),
        "xai" + "-" + ("F" * 20),
        ("9" * 9) + ":" + ("F" * 30),
    ]
    text = (
        " ".join(credentials)
        + " version=v0.20.0 commit=0123456789abcdef0123456789abcdef01234567 "
        "https://hermes-agent.nousresearch.com/docs"
    )

    redacted = module.redact(text)

    for credential in credentials:
        assert credential not in redacted
    assert redacted.count("[REDACTED_CREDENTIAL]") == len(credentials)
    assert "v0.20.0" in redacted
    assert "0123456789abcdef0123456789abcdef01234567" in redacted
    assert "https://hermes-agent.nousresearch.com/docs" in redacted


def test_source_status_redacts_fine_grained_github_token_constructed_at_runtime():
    module = load_module()
    credential = "github" + "_pat_" + ("A" * 24)

    redacted = module.redact("credential=" + credential)

    assert credential not in redacted
    assert "[REDACTED_CREDENTIAL]" in redacted


def test_source_status_redacts_escaped_multiline_assignment_values_whole():
    module = load_module()
    first_key = "OPENAI" + "_" + "API" + "_" + "KEY"
    second_key = "client" + "-" + "secret"
    text = (
        f'"{first_key}": "line-one \\\"quoted\\\" secret\\\\\\nline-two"\n'
        f"'{second_key}'='first line \\\'quoted\\\' secret\\\\\\nsecond line'"
    )

    redacted = module.redact(text)

    assert '"OPENAI_API_KEY": "[REDACTED]"' in redacted
    assert "'client-secret'='[REDACTED]'" in redacted
    for fragment in ["line-one", "quoted", "line-two", "first line", "second line"]:
        assert fragment not in redacted


def test_source_status_redacts_nonofficial_urls_and_keeps_only_exact_official_families():
    module = load_module()
    official = [
        "https://hermes-agent.nousresearch.com/docs",
        "https://hermes-agent.nousresearch.com/docs/setup",
        "https://github.com/NousResearch/hermes-agent",
        "https://github.com/NousResearch/hermes-agent/tree/main",
        "https://api.github.com/repos/NousResearch/hermes-agent/releases",
    ]
    https_scheme = "https" + "://"
    http_scheme = "http" + "://"
    query_key = "to" + "ken"
    private = [
        http_scheme + "github.com/NousResearch/hermes-agent",
        https_scheme + "evil.example.test/internal",
        https_scheme + "user:pass@github.com/NousResearch/hermes-agent",
        https_scheme + "github.com:8443/NousResearch/hermes-agent",
        https_scheme + "github.com/NousResearch/hermes-agent?" + query_key + "=FAKEURLSECRET",
        https_scheme + "github.com/NousResearch/hermes-agent#fragment-secret",
        https_scheme + "127.0.0.1:8080/status",
        https_scheme + "192.168.1.20/private",
        https_scheme + "[fd00::1]/private",
    ]

    redacted = module.redact(" ".join(official + private))

    for url in official:
        assert url in redacted
    for url in private:
        assert url not in redacted
    assert redacted.count("[REDACTED_URL]") == len(private)


def test_source_status_url_redaction_is_collision_safe_and_idempotent():
    module = load_module()
    private_url = "https" + "://private.example.test/path"
    text = (
        "literal __EMH_PUBLIC_URL_0__ __EMH_PUBLIC_URL_999__ "
        + private_url + " ./private/cache.txt"
    )

    redacted = module.redact(text)

    assert "__EMH_PUBLIC_URL_0__" in redacted
    assert "__EMH_PUBLIC_URL_999__" in redacted
    assert private_url not in redacted
    assert module.redact(redacted) == redacted
