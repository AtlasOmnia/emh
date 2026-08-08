#!/usr/bin/env python3
"""EMH break-glass collector — stdlib only, no Hermes imports.

Runs on a machine where Hermes may be broken or absent. Emits a redacted
machine baseline as JSON (stdout or --out FILE). Never reads credentials,
memories, raw logs, private paths, or configuration secrets.

Usage:
  python3 breakglass_collect.py --out baseline.json
"""

import argparse
import datetime
import json
import os
import platform
import shutil
import subprocess
import sys


def _run(command):
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=15
        )
        return (result.stdout or result.stderr).strip() or None
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=None, help="write baseline JSON to FILE")
    args = ap.parse_args()

    hermes_path = shutil.which("hermes")
    baseline = {
        "collected_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "disk": _run(["df", "-h"]) if os.name != "nt" else None,
        "hermes": {
            "on_path": hermes_path is not None,
            "version": _run(["hermes", "--version"]) if hermes_path else None,
            "home": os.environ.get("HERMES_HOME") or os.path.expanduser("~/.hermes"),
            "profiles": _run(["hermes", "profile", "list"]) if hermes_path else None,
        },
    }

    payload = json.dumps(baseline, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(payload)
        print("baseline written: " + args.out)
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
