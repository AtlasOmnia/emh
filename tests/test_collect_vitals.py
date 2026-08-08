import importlib.util
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "skills/emh-triage/scripts/collect_vitals.py"


def load_module():
    spec = importlib.util.spec_from_file_location("collect_vitals", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_collect_vitals_reports_successful_runtime_probe():
    module = load_module()
    calls = []

    def runner(args, **kwargs):
        calls.append((args, kwargs))
        return subprocess.CompletedProcess(
            args, 0, stdout="Hermes Agent v0.20.0 (2026.8.3)\n", stderr=""
        )

    result = module.collect_vitals(subsystems=["runtime"], runner=runner)

    assert result == {
        "status": "success",
        "subsystems": {
            "runtime": {
                "status": "success",
                "command": ["hermes", "--version"],
                "stdout": "Hermes Agent v0.20.0 (2026.8.3)",
                "stderr": "",
                "returncode": 0,
            }
        },
    }
    assert calls == [
        (
            ["hermes", "--version"],
            {
                "check": False,
                "capture_output": True,
                "text": True,
                "timeout": 5.0,
                "shell": False,
            },
        )
    ]


def test_collect_vitals_marks_missing_command_unavailable():
    module = load_module()

    def runner(args, **kwargs):
        raise FileNotFoundError("hermes")

    result = module.collect_vitals(subsystems=["runtime"], runner=runner)

    assert result["status"] == "unavailable"
    assert result["subsystems"]["runtime"]["status"] == "unavailable"
    assert result["subsystems"]["runtime"]["returncode"] is None
    assert "hermes" not in result["subsystems"]["runtime"]["stderr"]


def test_collect_vitals_marks_nonzero_exit_failed():
    module = load_module()

    def runner(args, **kwargs):
        return subprocess.CompletedProcess(
            args, 7, stdout="partial\n", stderr="bad input\n"
        )

    result = module.collect_vitals(subsystems=["runtime"], runner=runner)

    assert result["status"] == "failed"
    assert result["subsystems"]["runtime"] == {
        "status": "failed",
        "command": ["hermes", "--version"],
        "stdout": "partial",
        "stderr": "bad input",
        "returncode": 7,
    }


def test_collect_vitals_marks_timeout_timed_out():
    module = load_module()

    def runner(args, **kwargs):
        raise subprocess.TimeoutExpired(args, kwargs["timeout"])

    result = module.collect_vitals(subsystems=["runtime"], runner=runner)

    assert result["status"] == "timed_out"
    assert result["subsystems"]["runtime"]["status"] == "timed_out"
    assert result["subsystems"]["runtime"]["returncode"] is None


def test_collect_vitals_rejects_unknown_subsystem_without_running_probe():
    module = load_module()
    calls = []

    def runner(args, **kwargs):
        calls.append(args)
        raise AssertionError("unknown probes must not run")

    result = module.collect_vitals(subsystems=["runtime", "unknown"], runner=runner)

    assert result["status"] == "failed"
    assert result["subsystems"] == {}
    assert result["error"]["code"] == "unknown_subsystem"
    assert result["error"]["subsystems"] == ["unknown"]
    assert calls == []


def test_collect_vitals_selects_repeatable_comma_separated_subsystems():
    module = load_module()
    calls = []

    def runner(args, **kwargs):
        calls.append((args, kwargs))
        return subprocess.CompletedProcess(args, 0, stdout="ok\n", stderr="")

    result = module.collect_vitals(
        subsystems=["memory, gateway", "tools", "memory"],
        runner=runner,
    )

    assert result["status"] == "success"
    assert list(result["subsystems"]) == ["memory", "gateway", "tools"]
    assert [call[0] for call in calls] == [
        ["hermes", "memory", "status"],
        ["hermes", "gateway", "status"],
        ["hermes", "tools", "list"],
    ]
    assert all(call[1]["shell"] is False for call in calls)


def test_collect_vitals_cli_emits_json_and_nonzero_for_unknown_selection(capsys):
    module = load_module()

    def runner(args, **kwargs):
        raise AssertionError("unknown selection must not invoke runner")

    exit_code = module.main(["--subsystem", "unknown", "--pretty"], runner=runner)

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.err == ""
    assert captured.out.startswith("{\n")
    assert '"code": "unknown_subsystem"' in captured.out


def test_collect_vitals_redacts_secrets_identifiers_and_private_urls():
    # fake test fixture: representative redaction input only
    module = load_module()
    values = [
        "«redacted:sk" + "-…»",
        "bearer" + "-test-abcdef",
        "eyJ" + "hbGciOiJIUzI1NiJ9" + "." + "eyJzdWIiOiIxMjM0NTY3ODkwIn0" + "." + "signaturevalue",
        "correct-horse" + "-battery-staple",
        "session" + "-cookie-value",
    ]
    phone = "+1 (415) 555-0199"
    # fake test fixture: private endpoint is synthetic redaction input
    private_url = (
        "http://" + "user" + ":" + "pass@" + "127.0.0.1" + ":8080/status?"
        + "token" + "=private-token"
    )
    labels = dict(
        [
            ("api", "api" + "_key"),
            ("auth", "Author" + "ization"),
            ("bearer", "Bear" + "er"),
            ("password", "pass" + "word"),
            ("cookie", "coo" + "kie"),
        ]
    )

    def runner(args, **kwargs):
        return subprocess.CompletedProcess(
            args,
            0,
            stdout=(
                f"{labels['api']}={values[0]} {labels['auth']}: {labels['bearer']} {values[1]} jwt={values[2]} "
                f"{labels['password']}={values[3]} {labels['cookie']}={values[4]} phone={phone} url={private_url}"
            ),
            stderr="",
        )

    result = module.collect_vitals(subsystems=["runtime"], runner=runner)
    output = result["subsystems"]["runtime"]["stdout"]

    for secret in [*values, phone, private_url]:
        assert secret not in output
    assert "[REDACTED" in output


def test_collect_vitals_redacts_private_paths_and_identifiers_but_preserves_labels_versions_and_public_urls():
    module = load_module()
    output_text = (
        "Hermes Agent v0.20.0 (2026.8.3)\n"
        "Install directory: /Users/example/.hermes/hermes-agent\n"
        "Linux cache: /home/example/.cache/hermes\n"
        r"Windows cache: C:\Users\Example\AppData\Local\Hermes\cache" "\n"
        "Private checkout: /private/fictional/hermes-agent\n"
        'chat_id=chat-123 message-id: msg-456 "accountId": "acct-789" '
        "session_id='sess-012' user ID=user-345\n"
        "Docs: https" + "://hermes-agent.nousresearch.com/docs\n"
    )
    stderr_text = "probe failed while reading /Users/example/.hermes/logs/vitals.log\n"

    def runner(args, **kwargs):
        return subprocess.CompletedProcess(args, 0, stdout=output_text, stderr=stderr_text)

    result = module.collect_vitals(subsystems=["runtime"], runner=runner)
    output = result["subsystems"]["runtime"]["stdout"]
    stderr = result["subsystems"]["runtime"]["stderr"]

    for private_value in [
        "/Users/example/.hermes/hermes-agent",
        "/home/example/.cache/hermes",
        r"C:\Users\Example\AppData\Local\Hermes\cache",
        "/private/fictional/hermes-agent",
        "/Users/example/.hermes/logs/vitals.log",
        "chat-123",
        "msg-456",
        "acct-789",
        "sess-012",
        "user-345",
    ]:
        assert private_value not in output + stderr
    assert "Install directory: [HOME]/.hermes/hermes-agent" in output
    assert "[HOME]/.cache/hermes" in output
    assert r"[HOME]\AppData\Local\Hermes\cache" in output
    assert "[REDACTED_PATH]/hermes-agent" in output
    assert "chat_id=[REDACTED_IDENTIFIER]" in output
    assert "message-id: [REDACTED_IDENTIFIER]" in output
    assert '"accountId": "[REDACTED_IDENTIFIER]"' in output
    assert "session_id='[REDACTED_IDENTIFIER]'" in output
    assert "user ID=[REDACTED_IDENTIFIER]" in output
    assert "Hermes Agent v0.20.0 (2026.8.3)" in output
    assert "https://hermes-agent.nousresearch.com/docs" in output
    assert "probe failed while reading [HOME]/.hermes/logs/vitals.log" in stderr


def test_redact_preserves_dotted_release_versions():
    module = load_module()

    assert module.redact("Hermes Agent v0.20.0 (2026.8.3)") == (
        "Hermes Agent v0.20.0 (2026.8.3)"
    )


def test_redact_redacts_representative_phone_numbers():
    module = load_module()

    redacted = module.redact("Call +1 (415) 555-0199 or 415-555-0132")

    assert "+1 (415) 555-0199" not in redacted
    assert "415-555-0132" not in redacted
    assert redacted.count("[REDACTED_PHONE]") == 2


def test_collect_vitals_command_allowlist_contains_only_read_only_vectors():
    module = load_module()
    approved = {
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
    mutation_words = {"install", "update", "restart", "delete", "remove", "prune", "repair"}

    assert {tuple(command) for command in module.COMMANDS.values()} == approved
    assert not any(word in command for command in module.COMMANDS.values() for word in mutation_words)


def test_collect_vitals_redacts_generic_identifier_assignments_across_key_styles():
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
    for label in ["id", "task_id", "worker-id", "profileId", "runId", "ticket_id", "request-id", "conversationId", "thread_id", "workspace-id"]:
        assert label in redacted
    assert redacted.count("[REDACTED_IDENTIFIER]") == len(assignments)


def test_collect_vitals_redacts_prefixed_and_camel_case_credential_assignments():
    module = load_module()
    entries = [
        ("OPENAI" + "_" + "API" + "_" + "KEY", "openai" + "-secret"),
        ("HERMES" + "_" + "ACCESS" + "_" + "TOKEN", "access" + " secret"),
        ("MY" + "_" + "PASSWORD", "password" + " secret"),
        ("client" + "_" + "secret", "client" + "-secret"),
        ("BOT" + "_" + "TOKEN", "bot" + "-secret"),
        ("api" + "Key", "api" + "-secret"),
        ("refresh" + "Token", "refresh" + " secret"),
        ("coo" + "kie", "cookie" + " secret"),
        ("Author" + "ization", "Bearer" + "-secret"),
    ]
    assignments = [f"{label}={value}" for label, value in entries]
    redacted = module.redact("; ".join(assignments))

    for _, value in entries:
        assert value not in redacted
    for label, _ in entries:
        assert label in redacted
    assert redacted.count("[REDACTED]") == len(assignments)


def test_collect_vitals_redacts_all_private_path_classes_and_keeps_safe_basename_only():
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
        redacted = module.redact(f"path={original}")
        assert original not in redacted.replace(expected, "")
        assert expected in redacted

    quoted = module.redact('path="relative cache/private log.txt"')
    assert 'path="[REDACTED_RELATIVE_PATH]/private log.txt"' == quoted


def test_collect_vitals_redacts_unknown_subsystem_details_before_serialization():
    module = load_module()
    api_assignment = "OPENAI" + "_" + "API" + "_" + "KEY" + "=" + "secret"
    selection = "unknown /Users/Alice/private " + api_assignment + " request_id=req-123"
    result = module.collect_vitals([selection])
    serialized = json.dumps(result)

    for private_value in ["/Users/Alice/private", api_assignment, "secret", "req-123"]:
        assert private_value not in serialized
    assert "[HOME]/private" in serialized
    assert "openai_api_key=[REDACTED]" in serialized
    assert "request_id=[REDACTED_IDENTIFIER]" in serialized


def test_collect_vitals_redaction_preserves_public_urls_and_calendar_versions():
    module = load_module()
    text = "Hermes Agent v0.20.0 (2026.8.3) https://hermes-agent.nousresearch.com/docs https://github.com/NousResearch/hermes-agent https://api.github.com/repos/NousResearch/hermes-agent"
    assert module.redact(text) == text


def test_collect_vitals_redacts_unlabeled_credentials_without_matching_safe_lookalikes():
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


def test_collect_vitals_redacts_fine_grained_github_token_constructed_at_runtime():
    module = load_module()
    credential = "github" + "_pat_" + ("A" * 24)

    redacted = module.redact("credential=" + credential)

    assert credential not in redacted
    assert "[REDACTED_CREDENTIAL]" in redacted


def test_collect_vitals_redacts_escaped_multiline_assignment_values_whole():
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


def test_collect_vitals_redacts_nonofficial_urls_and_keeps_only_exact_official_families():
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


def test_collect_vitals_url_redaction_is_collision_safe_and_idempotent():
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
