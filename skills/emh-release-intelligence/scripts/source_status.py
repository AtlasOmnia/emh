#!/usr/bin/env python3
"""Read-only Hermes install and release status helpers."""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from urllib.parse import urlsplit
from typing import Any, Callable, Mapping, Sequence


VERSION_COMMAND = ("hermes", "version")
RELEASE_API_URL = "https://api.github.com/repos/NousResearch/hermes-agent/releases/latest"
USER_AGENT = "EMH/0.1.0"
DEFAULT_TIMEOUT = 5.0
MIN_TIMEOUT = 0.1
MAX_TIMEOUT = 60.0
MAX_RESPONSE_BYTES = 64 * 1024
Runner = Callable[..., subprocess.CompletedProcess[Any]]

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


_RELEASE_TAG = re.compile(r"v?(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)")
_PUBLISHED_AT = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?Z")


def _is_release_url(url: str, tag: str) -> bool:
    if not _is_official_url(url):
        return False
    return url == f"https://github.com/NousResearch/hermes-agent/releases/tag/{tag}"


def _is_valid_published_at(value: str) -> bool:
    if _PUBLISHED_AT.fullmatch(value) is None:
        return False
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return False
    return True


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


def redact(value: object) -> str:
    """Return diagnostic text with secrets and private identifiers removed."""

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


def _text(value: object) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value or "")


def _parse_hermes_version_raw(output: str) -> dict[str, object]:
    """Parse Hermes version output while retaining the path for internal probing."""

    version_match = re.search(r"^Hermes Agent v?([0-9][\w.-]*)", output, re.MULTILINE)
    directory_match = re.search(r"^Install directory:\s*(.*?)\s*$", output, re.MULTILINE)
    method_match = re.search(r"^Install method:\s*(\S+)\s*$", output, re.MULTILINE)
    update_match = re.search(r"^Update available:\s*(.*?)\s*(?:—|--|$)", output, re.MULTILINE)
    up_to_date = re.search(r"^Up to date\b", output, re.MULTILINE | re.IGNORECASE)
    if not (version_match and directory_match and method_match):
        raise ValueError("unrecognized hermes version output")
    update_available = bool(update_match)
    update_status = update_match.group(1).strip() if update_match else ("up to date" if up_to_date else "unknown")
    return {
        "version": version_match.group(1),
        "install_directory": directory_match.group(1),
        "install_method": method_match.group(1).lower(),
        "update_status": redact(update_status),
        "update_available": update_available,
    }


def parse_hermes_version(output: str) -> dict[str, object]:
    """Parse Hermes version output without exposing the raw install path."""

    parsed = _parse_hermes_version_raw(output)
    parsed["install_directory"] = _summarize_path(str(parsed["install_directory"]))
    return parsed


parse_version_output = parse_hermes_version


def _result_error(code: str, message: str) -> dict[str, object]:
    return {"status": "failed", "error": {"code": code, "message": redact(message)}}


def _validate_timeout(timeout: float) -> float | None:
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
        return None
    value = float(timeout)
    if not math.isfinite(value) or not MIN_TIMEOUT <= value <= MAX_TIMEOUT:
        return None
    return value


def summarize_git(path: str, *, runner: Runner = subprocess.run, timeout: float = DEFAULT_TIMEOUT) -> dict[str, object]:
    """Summarize a Git checkout without returning porcelain filenames."""

    timeout_value = _validate_timeout(timeout)
    if timeout_value is None:
        return _result_error("invalid_timeout", "Invalid command timeout")
    prefix = ["git", "-C", path]
    try:
        commit_result = runner(
            prefix + ["rev-parse", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_value,
            shell=False,
        )
        if commit_result.returncode != 0:
            return _result_error("git_failed", "Git commit lookup failed")
        commit = _text(commit_result.stdout).strip()
        if not re.fullmatch(r"[0-9a-fA-F]{7,64}", commit):
            return _result_error("git_failed", "Git returned an invalid commit identifier")
        status_result = runner(
            prefix + ["status", "--porcelain=v1", "-z"],
            check=False,
            capture_output=True,
            text=False,
            timeout=timeout_value,
            shell=False,
        )
        if status_result.returncode != 0:
            return _result_error("git_failed", "Git status lookup failed")
        raw_status = status_result.stdout
        if isinstance(raw_status, str):
            entries = [item for item in raw_status.split("\0") if item]
        else:
            entries = [item for item in raw_status.split(b"\0") if item]
        return {
            "status": "success",
            "commit": commit,
            "clean": not entries,
            "change_count": len(entries),
        }
    except subprocess.TimeoutExpired:
        return {"status": "timed_out"}
    except FileNotFoundError:
        return {"status": "unavailable"}
    except (OSError, subprocess.SubprocessError):
        return {"status": "failed"}


def parse_release_payload(payload: Mapping[str, object]) -> dict[str, str]:
    """Validate and normalize the official GitHub latest-release payload."""

    required = ("tag_name", "name", "html_url", "published_at")
    if any(not isinstance(payload.get(key), str) or not payload[key] for key in required):
        raise ValueError("malformed release payload")
    tag = str(payload["tag_name"])
    name = str(payload["name"])
    html_url = str(payload["html_url"])
    published_at = str(payload["published_at"])
    if (
        _RELEASE_TAG.fullmatch(tag) is None
        or not _is_release_url(html_url, tag)
        or not _is_valid_published_at(published_at)
    ):
        raise ValueError("malformed release payload")
    return {
        "tag": tag,
        "name": redact(name),
        "html_url": html_url,
        "published_at": published_at,
        "version": tag.removeprefix("v"),
    }


def fetch_latest_release(
    *,
    timeout: float = DEFAULT_TIMEOUT,
    urlopen: Callable[..., Any] | None = None,
) -> dict[str, object]:
    """Fetch only bounded metadata from the official latest-release endpoint."""

    timeout_value = _validate_timeout(timeout)
    if timeout_value is None:
        return _result_error("invalid_timeout", "Invalid network timeout")
    opener = urlopen or urllib.request.urlopen
    request = urllib.request.Request(
        RELEASE_API_URL,
        headers={"Accept": "application/vnd.github+json", "User-Agent": USER_AGENT},
        method="GET",
    )
    try:
        with opener(request, timeout=timeout_value) as response:
            status_code = getattr(response, "status", 200)
            if status_code >= 400:
                return _result_error("http_error", "Official release endpoint returned an error")
            body = response.read(MAX_RESPONSE_BYTES + 1)
            if len(body) > MAX_RESPONSE_BYTES:
                return _result_error("response_too_large", "Official release response exceeded the byte limit")
        payload = json.loads(_text(body))
        if not isinstance(payload, dict):
            raise ValueError("malformed release payload")
        return {"status": "success", "release": parse_release_payload(payload)}
    except (TimeoutError, socket_timeout_type()):
        return {"status": "timed_out"}
    except urllib.error.HTTPError:
        return _result_error("http_error", "Official release endpoint returned an error")
    except urllib.error.URLError:
        return {"status": "unavailable"}
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError, TypeError):
        return _result_error("malformed_payload", "Official release response was malformed")
    except OSError:
        return {"status": "unavailable"}


def socket_timeout_type() -> type[BaseException]:
    """Return the socket timeout type without importing platform-specific modules eagerly."""

    import socket

    return socket.timeout


def collect_status(
    *,
    timeout: float = DEFAULT_TIMEOUT,
    runner: Runner = subprocess.run,
    offline: bool = False,
    release_fetcher: Callable[..., dict[str, object]] = fetch_latest_release,
) -> dict[str, object]:
    """Collect install, optional Git, and official release metadata read-only."""

    timeout_value = _validate_timeout(timeout)
    if timeout_value is None:
        return {"status": "failed", "error": {"code": "invalid_timeout", "message": "Invalid timeout"}}
    try:
        version_result = runner(
            list(VERSION_COMMAND),
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_value,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        return {"status": "timed_out", "current": None, "latest_release": {"status": "offline"}}
    except FileNotFoundError:
        return {"status": "unavailable", "current": None, "latest_release": {"status": "offline"}}
    except (OSError, subprocess.SubprocessError):
        return {"status": "failed", "current": None, "latest_release": {"status": "offline"}}
    if version_result.returncode != 0:
        return {"status": "failed", "current": None, "latest_release": {"status": "offline"}}
    try:
        current_raw = _parse_hermes_version_raw(_text(version_result.stdout))
    except ValueError:
        return {"status": "failed", "current": None, "latest_release": {"status": "offline"}}
    current = dict(current_raw)
    current["install_directory"] = _summarize_path(str(current_raw["install_directory"]))

    git_result: dict[str, object] | None = None
    raw_install_directory = str(current_raw["install_directory"])
    if current_raw["install_method"] == "git" and raw_install_directory:
        git_result = summarize_git(raw_install_directory, runner=runner, timeout=timeout_value)
    release_result: dict[str, object]
    if offline:
        release_result = {"status": "offline"}
    else:
        release_result = release_fetcher(timeout=timeout_value)
    states = {"success", release_result.get("status", "failed")}
    if git_result is not None:
        states.add(str(git_result.get("status", "failed")))
    if "failed" in states:
        overall = "failed"
    elif "timed_out" in states:
        overall = "timed_out"
    elif "unavailable" in states or "offline" in states:
        overall = "unavailable"
    else:
        overall = "success"
    return {"status": overall, "current": current, "git": git_result, "latest_release": release_result}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument("--offline", action="store_true", help="Do not query the official release API")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    runner: Runner = subprocess.run,
    release_fetcher: Callable[..., dict[str, object]] = fetch_latest_release,
) -> int:
    try:
        args = _parser().parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    result = collect_status(
        timeout=args.timeout,
        runner=runner,
        offline=args.offline,
        release_fetcher=release_fetcher,
    )
    json.dump(result, sys.stdout, indent=2 if args.pretty else None, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
