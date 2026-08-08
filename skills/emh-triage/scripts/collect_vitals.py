#!/usr/bin/env python3
"""Collect bounded, read-only Hermes vitals without exposing private data."""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
from urllib.parse import urlsplit
from typing import Callable, Mapping, Sequence


COMMANDS: Mapping[str, tuple[str, ...]] = {
    "runtime": ("hermes", "--version"),
    "memory": ("hermes", "memory", "status"),
    "kanban": ("hermes", "kanban", "stats"),
    "plugins": ("hermes", "plugins", "list"),
    "gateway": ("hermes", "gateway", "status"),
    "profiles": ("hermes", "profile", "list"),
    "sessions": ("hermes", "sessions", "stats"),
    "skills": ("hermes", "skills", "list"),
    "tools": ("hermes", "tools", "list"),
}
DEFAULT_TIMEOUT = 5.0
MIN_TIMEOUT = 0.1
MAX_TIMEOUT = 60.0
Runner = Callable[..., subprocess.CompletedProcess[str]]

_ASSIGNMENT_PREFIX = re.compile(
    r'''(?P<prefix>(?P<key_quote>["']?)(?P<key>[A-Za-z][A-Za-z0-9_-]*)(?P=key_quote)\s*[:=]\s*)(?!/)'''
)
_BEARER = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+")
_JWT = re.compile(r"\beyJ[A-Za-z0-9_-]{4,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b")
_PHONE = re.compile(r"(?<!\w)\+?[\d ()\-]{10,25}(?!\w)")
_EMAIL = re.compile(r"(?i)(?<![\w@])([\w.+-]+@[\w.-]+\.[a-z]{2,})(?![\w@])")
_INSTALL_DIRECTORY_LINE = re.compile(r"(?im)^(?P<prefix>\s*Install directory:\s*)(?P<path>[^\r\n]+?)\s*$")
_QUOTED_VALUE = re.compile(r'''(?P<quote>["'])(?P<value>.*?)(?P=quote)''')
_URL_TOKEN = re.compile(r'''(?i)\bhttps?://[^\s<>'"`,;)}]+''')
_PATH_TOKEN = re.compile(
    r"(?<![A-Za-z0-9:/\.\-\]])(?<!]/)(?<!]\\)(?P<path>(?:[A-Za-z]:[\\/]+|\\\\|//|~/|\$HOME[\\/]|%USERPROFILE%[\\/]|/|\.\.?[\\/]|[A-Za-z0-9_.-]+[\\/])[^\s<>'\"`,;\)\]}]+)"
)
_CREDENTIAL = re.compile(
    r"(?<![A-Za-z0-9])(?:"
    r"sk-(?:proj-|ant-)?[A-Za-z0-9_-]{16,}|"
    r"github_pat_[A-Za-z0-9_]{16,}|"
    r"gh[pousr]_[A-Za-z0-9_]{16,}|"
    r"(?:AKIA|ASIA)[A-Z0-9]{16,}|"
    r"AIza[A-Za-z0-9_-]{16,}|"
    r"hf_[A-Za-z0-9]{16,}|"
    r"xox[a-z]+-[A-Za-z0-9-]{16,}|"
    r"xai-[A-Za-z0-9_-]{16,}|"
    r"\d{8,10}:[A-Za-z0-9_-]{30,}"
    r")(?![A-Za-z0-9_-])"
)


def _normalised_key(key: str) -> str:
    return re.sub(r"[-_]", "", key).lower()


def _is_secret_key(key: str) -> bool:
    normalised = _normalised_key(key)
    return any(marker in normalised for marker in (
        "apikey", "accesstoken", "refreshtoken", "authorization", "bearer",
        "password", "passwd", "secret", "cookie", "oauth", "token",
    ))


def _is_identifier_key(key: str) -> bool:
    normalised = _normalised_key(key)
    return normalised == "id" or normalised.endswith("id")


def _is_path_key(key: str) -> bool:
    normalised = _normalised_key(key)
    return (
        normalised == "path"
        or normalised.endswith("path")
        or normalised in {"directory", "dir", "file", "filename", "location", "cwd", "home", "workspace"}
    )


def _summarize_path(path: str) -> str:
    candidate = path.strip()
    if len(candidate) >= 2 and candidate[0] == candidate[-1] and candidate[0] in "\\\"'":
        candidate = candidate[1:-1]
    if re.match(r"(?i)https?://", candidate) or re.match(r"^\[[A-Z0-9_]+\](?:[\\/].*)?$", candidate):
        return candidate
    home_match = re.match(r"^/(?:Users|home)/[^/\\]+(?P<rest>[\\/].*)?$", candidate, re.IGNORECASE)
    if home_match:
        return "[HOME]" + (home_match.group("rest") or "")
    windows_home_match = re.match(
        r"^[A-Za-z]:[\\/]+Users[\\/]+[^\\/]+(?P<rest>[\\/].*)?$", candidate, re.IGNORECASE
    )
    if windows_home_match:
        return "[HOME]" + (windows_home_match.group("rest") or "")
    if re.match(r"^(?:~/|\$HOME[\\/]|%USERPROFILE%[\\/])", candidate, re.IGNORECASE):
        if candidate.startswith("~"):
            return "[HOME]" + candidate[1:]
        marker = re.match(r"^(?:\$HOME|%USERPROFILE%)(?P<rest>[\\/].*)$", candidate, re.IGNORECASE)
        return "[HOME]" + (marker.group("rest") if marker else "")
    is_absolute = candidate.startswith(("/", "\\\\", "//")) or bool(re.match(r"^[A-Za-z]:[\\/]", candidate))
    is_relative = candidate.startswith(("./", "../", ".\\", "..\\")) or (not is_absolute and ("/" in candidate or "\\" in candidate))
    if is_absolute or is_relative:
        stripped = candidate.rstrip("\\/")
        basename = re.split(r"[\\/]", stripped)[-1]
        marker = "[REDACTED_RELATIVE_PATH]" if is_relative and not is_absolute else "[REDACTED_PATH]"
        separator = "\\" if "\\" in candidate and not candidate.startswith("/") else "/"
        return f"{marker}{separator}{basename}" if basename else marker
    return f"[REDACTED_RELATIVE_PATH]/{candidate}" if candidate else candidate


def _looks_like_path(value: str) -> bool:
    candidate = value.strip()
    if re.match(r"(?i)https?://", candidate):
        return False
    return bool(
        re.match(r"^(?:/|\\\\|//|[A-Za-z]:[\\/]|~/|\$HOME[\\/]|%USERPROFILE%[\\/]|\.\.?[\\/])", candidate, re.IGNORECASE)
        or "/" in candidate
        or "\\" in candidate
    )


def _read_assignment_value(text: str, start: int) -> tuple[int, str, str, bool]:
    quote = text[start] if start < len(text) and text[start] in "\"'" else ""
    if not quote:
        end = start
        while end < len(text) and text[end] not in " \t\r\n,;}]":
            end += 1
        return end, text[start:end], "", True
    end = start + 1
    while end < len(text):
        if text[end] == "\\":
            end += 2
            continue
        if text[end] == quote:
            return end + 1, text[start + 1:end], quote, True
        end += 1
    return len(text), text[start + 1 :], quote, False


def _redact_assignments(text: str) -> str:
    output: list[str] = []
    cursor = 0
    for match in _ASSIGNMENT_PREFIX.finditer(text):
        if match.start() < cursor:
            continue
        value_start = match.end()
        if value_start >= len(text):
            continue
        value_end, raw_value, value_quote, closed = _read_assignment_value(text, value_start)
        if value_end <= value_start:
            continue
        key = match.group("key")
        marker = "[REDACTED]" if _is_secret_key(key) else "[REDACTED_IDENTIFIER]" if _is_identifier_key(key) else None
        output.append(text[cursor : match.start()])
        prefix = match.group("prefix")
        if marker is not None:
            closing_quote = value_quote if value_quote and closed else ""
            output.append(prefix + value_quote + marker + closing_quote)
        elif _is_path_key(key):
            output.append(prefix + value_quote + _summarize_path(raw_value) + (value_quote if value_quote and closed else ""))
        else:
            output.append(text[match.start() : value_end])
        cursor = value_end
    output.append(text[cursor:])
    return "".join(output)


def _is_official_url(url: str) -> bool:
    try:
        parsed = urlsplit(url)
        if parsed.scheme.lower() != "https" or parsed.username is not None or parsed.password is not None:
            return False
        if parsed.query or parsed.fragment or parsed.port is not None:
            return False
        host = parsed.hostname.lower() if parsed.hostname else ""
    except ValueError:
        return False
    path = parsed.path
    return (
        (host == "hermes-agent.nousresearch.com" and (path == "/docs" or path.startswith("/docs/")))
        or (host == "github.com" and (path == "/NousResearch/hermes-agent" or path.startswith("/NousResearch/hermes-agent/")))
        or (host == "api.github.com" and (path == "/repos/NousResearch/hermes-agent" or path.startswith("/repos/NousResearch/hermes-agent/")))
    )


def _redact_urls(text: str) -> str:
    return _URL_TOKEN.sub(lambda match: match.group(0) if _is_official_url(match.group(0)) else "[REDACTED_URL]", text)


def _transform_non_url_spans(text: str, transform: Callable[[str], str]) -> str:
    output: list[str] = []
    cursor = 0
    for match in _URL_TOKEN.finditer(text):
        output.append(transform(text[cursor : match.start()]))
        url = match.group(0)
        output.append(url if _is_official_url(url) else "[REDACTED_URL]")
        cursor = match.end()
    output.append(transform(text[cursor:]))
    return "".join(output)


def _redact_paths(text: str) -> str:
    text = _transform_non_url_spans(text, lambda segment: _redact_path_segment(segment))
    return text


def _redact_path_segment(text: str) -> str:
    def replace_directory(match: re.Match[str]) -> str:
        return match.group("prefix") + _summarize_path(match.group("path"))

    text = _INSTALL_DIRECTORY_LINE.sub(replace_directory, text)

    def replace_quoted(match: re.Match[str]) -> str:
        value = match.group("value")
        return match.group("quote") + _summarize_path(value) + match.group("quote") if _looks_like_path(value) else match.group(0)

    text = _QUOTED_VALUE.sub(replace_quoted, text)
    text = _PATH_TOKEN.sub(lambda match: _summarize_path(match.group("path")), text)
    return text


def redact(value: str | None) -> str:
    """Redact secrets, identifiers, and private endpoints from diagnostic text."""

    text = "" if value is None else str(value)
    text = _redact_urls(text)
    text = _transform_non_url_spans(text, lambda segment: _BEARER.sub("Bearer [REDACTED]", segment))
    text = _transform_non_url_spans(text, _redact_assignments)
    text = _transform_non_url_spans(text, lambda segment: _JWT.sub("[REDACTED_JWT]", segment))
    text = _transform_non_url_spans(text, lambda segment: _CREDENTIAL.sub("[REDACTED_CREDENTIAL]", segment))
    text = _transform_non_url_spans(
        text,
        lambda segment: _PHONE.sub(
            lambda match: "[REDACTED_PHONE]"
            if 10 <= sum(character.isdigit() for character in match.group(0)) <= 15
            else match.group(0),
            segment,
        ),
    )
    text = _transform_non_url_spans(text, lambda segment: _EMAIL.sub("[REDACTED_IDENTIFIER]", segment))
    return _redact_paths(text)


def _normalise_subsystems(subsystems: Sequence[str] | None) -> list[str]:
    if subsystems is None:
        return ["runtime"]
    selected: list[str] = []
    for item in subsystems:
        for name in str(item).split(","):
            name = name.strip().lower()
            if name and name not in selected:
                selected.append(name)
    return selected


def _redact_detail(value: object) -> object:
    if isinstance(value, str):
        return redact(value)
    if isinstance(value, Mapping):
        return {str(key): _redact_detail(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_redact_detail(item) for item in value]
    return value


def _error(code: str, message: str, **details: object) -> dict[str, object]:
    error: dict[str, object] = {"code": code, "message": redact(message)}
    error.update({key: _redact_detail(value) for key, value in details.items()})
    return error


def _aggregate_status(statuses: set[str]) -> str:
    if not statuses:
        return "unavailable"
    if statuses == {"success"}:
        return "success"
    if "failed" in statuses:
        return "failed"
    if "timed_out" in statuses:
        return "timed_out"
    return "unavailable"


def _output_text(value: object) -> str:
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    return redact(str(value or "").strip())


def collect_vitals(
    subsystems: Sequence[str] | None = None,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    runner: Runner = subprocess.run,
) -> dict[str, object]:
    """Run only the fixed read-only probes selected by the caller."""

    selected = _normalise_subsystems(subsystems)
    unknown = [name for name in selected if name not in COMMANDS]
    if unknown:
        return {
            "status": "failed",
            "subsystems": {},
            "error": _error(
                "unknown_subsystem",
                "Unknown subsystem selection",
                subsystems=unknown,
            ),
        }
    if not selected:
        return {
            "status": "failed",
            "subsystems": {},
            "error": _error("no_subsystems", "At least one subsystem is required"),
        }
    if not isinstance(timeout, (int, float)) or isinstance(timeout, bool):
        return {
            "status": "failed",
            "subsystems": {},
            "error": _error("invalid_timeout", "Timeout must be a number"),
        }
    if not math.isfinite(float(timeout)) or not MIN_TIMEOUT <= float(timeout) <= MAX_TIMEOUT:
        return {
            "status": "failed",
            "subsystems": {},
            "error": _error(
                "invalid_timeout",
                f"Timeout must be between {MIN_TIMEOUT:g} and {MAX_TIMEOUT:g} seconds",
            ),
        }

    results: dict[str, dict[str, object]] = {}
    for subsystem in selected:
        command = list(COMMANDS[subsystem])
        try:
            completed = runner(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=float(timeout),
                shell=False,
            )
        except FileNotFoundError:
            results[subsystem] = {
                "status": "unavailable",
                "command": command,
                "stdout": "",
                "stderr": "",
                "returncode": None,
            }
            continue
        except PermissionError:
            results[subsystem] = {
                "status": "unavailable",
                "command": command,
                "stdout": "",
                "stderr": "",
                "returncode": None,
            }
            continue
        except subprocess.TimeoutExpired:
            results[subsystem] = {
                "status": "timed_out",
                "command": command,
                "stdout": "",
                "stderr": "",
                "returncode": None,
            }
            continue
        except OSError as exc:
            results[subsystem] = {
                "status": "unavailable",
                "command": command,
                "stdout": "",
                "stderr": redact(str(exc)),
                "returncode": None,
            }
            continue
        except subprocess.SubprocessError as exc:
            results[subsystem] = {
                "status": "failed",
                "command": command,
                "stdout": "",
                "stderr": redact(str(exc)),
                "returncode": None,
            }
            continue

        returncode = completed.returncode
        results[subsystem] = {
            "status": "success" if returncode == 0 else "failed",
            "command": command,
            "stdout": _output_text(completed.stdout),
            "stderr": _output_text(completed.stderr),
            "returncode": returncode,
        }

    return {"status": _aggregate_status({item["status"] for item in results.values()}), "subsystems": results}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-s",
        "--subsystem",
        "--subsystems",
        action="append",
        dest="subsystems",
        help="Subsystem name; repeat or separate names with commas (default: runtime)",
    )
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    return parser


def main(argv: Sequence[str] | None = None, *, runner: Runner = subprocess.run) -> int:
    try:
        args = _parser().parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    result = collect_vitals(args.subsystems, timeout=args.timeout, runner=runner)
    json.dump(result, sys.stdout, indent=2 if args.pretty else None, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
