#!/usr/bin/env python3
"""EMH upstream knowledge probe — stdlib only, read-only.

Compares the installed EMH distribution version against the published
GitHub repo, and optionally fetches one repository file's raw content for
use as labeled upstream context. Never installs, never updates, never
writes anything. Fail-closed: network errors are a diagnostic result.

Usage:
  python3 upstream_check.py --installed 0.2.5
  python3 upstream_check.py --fetch skills/emh-gateway-diagnostics/SKILL.md
  python3 upstream_check.py --offline --installed 0.2.5
"""

import argparse
import json
import sys
import urllib.request

BASE = "https://raw.githubusercontent.com/AtlasOmnia/emh/main/"
DISTRIBUTION = "distribution.yaml"
TIMEOUT = 15


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "emh-upstream-probe"})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return response.read().decode("utf-8", errors="replace")


def upstream_version():
    text = fetch(BASE + DISTRIBUTION)
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("version:"):
            return line.split(":", 1)[1].strip()
    return "unknown"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--installed", default="", help="installed distribution version")
    parser.add_argument("--fetch", default="", help="repo-relative path to fetch (read-only)")
    parser.add_argument("--offline", action="store_true", help="never touch the network")
    args = parser.parse_args()

    if args.offline:
        print(json.dumps({"status": "unavailable", "reason": "offline mode"}))
        return 0

    try:
        if args.fetch:
            path = args.fetch
            if path.startswith("/") or ".." in path.split("/"):
                print(json.dumps({"status": "error", "reason": "invalid path"}))
                return 0
            print(fetch(BASE + path))
        else:
            upstream = upstream_version()
            print(json.dumps({
                "status": "ok",
                "installed": args.installed or "unknown",
                "upstream": upstream,
                "update_available": bool(args.installed) and args.installed != upstream,
            }))
    except Exception as exc:  # network failures are a diagnostic result, not a crash
        print(json.dumps({"status": "error", "reason": type(exc).__name__}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
