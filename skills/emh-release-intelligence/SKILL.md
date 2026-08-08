---
name: emh-release-intelligence
description: Use when a Hermes installation needs a read-only version, source, Git-state, or official-release comparison before discussing an update.
version: 0.1.0
author: Jonathan Rivera
license: UNLICENSED
platforms: [linux, macos, windows]
---

# EMH release intelligence

Use `skills/emh-release-intelligence/scripts/source_status.py` to summarize installed version, path/method, Git commit/clean state, and official latest-release metadata. This is evidence gathering, not an update mechanism.

## Workflow

1. Record **Complaint**, **Vitals**, **Differential diagnosis**, **Confirmed diagnosis**, **Treatment**, **Post-treatment verification**, and **Discharge summary or escalation packet** in that order.
2. Run `python3 skills/emh-release-intelligence/scripts/source_status.py --offline` for local evidence first. Without `--offline`, the script queries only the bounded official latest-release metadata endpoint; use that only when network access is explicitly acceptable.
3. Compare installed version, install method, source path summary, and Git state with the current official release. Current docs may be newer than the runtime. Identify a **Known upstream fix** only from official, version-matched evidence.
4. Label claims **Observed**, **Reproduced**, **Confirmed in installed source**, **Officially documented**, **Known upstream fix**, or **Hypothesis**. Newer does not mean necessary.

## Safety boundaries

Never fetch source, update, upgrade, reset, checkout, stash, clean, push, or alter the installation automatically. Do not disclose private install paths, remotes, credentials, or raw command output. A proposed update requires explicit approval, backup/rollback planning, and a post-treatment verification.

## Pitfalls

- Equating a newer release with a required update.
- Calling a community workaround a Known upstream fix.
- Treating Git dirty state as proof of the cause.
- Querying release metadata when offline evidence is sufficient.

## Verification

- `source_status.py` output is bounded and redacted.
- Installed-vs-current comparison includes version, method, and Git state where available.
- Official release evidence is adjacent to the claim and version-matched.
- No update or source mutation occurred.

Case record labels: Complaint; Vitals; Differential diagnosis; Confirmed diagnosis; Treatment; Post-treatment verification; Discharge summary or escalation packet.

Evidence labels: Observed; Reproduced; Confirmed in installed source; Officially documented; Known upstream fix; Hypothesis.
