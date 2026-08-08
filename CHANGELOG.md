# Changelog

All notable changes to the local EMH distribution candidate are recorded here. This repository is `UNLICENSED`; changelog entries do not represent a published release.

## 0.2.0 candidate — 2026-08-07

### Baseline

- Froze the campaign at commit `8fa0c3e3d8d34ff2a593c38bd150f978268ad69f`, tree `114aa648b7a5042f56f1f3fc87307a44aff3ba15`.
- Re-ran the unmodified suite: `127 passed`.
- Confirmed `main`, clean tracked/untracked state, one worktree, no Git locks, no remotes, no tags, and no competing repository writer.

### Added

- Added a portable responsibility coverage matrix and explicit overlap/handoff rules.
- Added four justified class-level diagnostic umbrellas:
  - `emh-interface-diagnostics`
  - `emh-tool-runtime-diagnostics`
  - `emh-environment-diagnostics`
  - `emh-update-recovery`
- Added exact twelve-skill inventory/version assertions, trigger and counter-trigger checks, command allowlists, domain classification checks, escalation-packet requirements, isolated test-home enforcement, and a fail-closed network guard.
- Added a distribution-owned `emh` skin for coordinated CLI, TUI, and Desktop presentation with 43 explicit colors and original diagnostic branding.

### Changed

- Advanced the distribution to `0.2.0` while retaining `0.1.0` for untouched v0.1 skills and assigning `0.2.0` to the four new capability classes.
- Expanded the README, subsystem map, and official source index for the new interfaces, tool-runtime, environment, and update-recovery routes.
- Changed the canonical opening to “Please state the nature of your Hermes emergency.” and added restrained, scope-aware holographic quips.
- Tightened the script-mode gate from owner-executable to exact mode `755`.

### TDD and candidate gates

- RED/GREEN slices covered missing inventory/frontmatter, complete workflow/safety/escalation content, semantic command/domain routing, isolated-home/network enforcement, release-surface reconciliation, canonical voice, and skin distribution.
- Final exact-archive suite at product candidate `a100f50d702c9c173a5bbb3eb4e7778698a6f058`: `153 passed`.
- Every repository script compiles with the Hermes Python runtime and remains mode `755`.
- `git diff --check` and the direct repository public-safety scanner pass with zero findings.
- Tests run with an isolated Hermes home and deny unexpected Python socket/URL transports.
- Exact-archive disposable install, update, and delete passed at `c39d1929590c97cea43b03af5abffc99931dd8e5`; the installed profile discovered the skin, preserved its SHA-256 `f8e9f1ac6ede1151b3b6a7c37d8c52d2f206d9473a3034a79f575ef2b830841e`, restored a tampered skin during update, preserved user configuration, and did not activate the skin or touch the live Hermes home.

### Local commits

- `fcb2638b098a1afe2bb7d0ecf3612987f2d616c5` — `docs: add v0.2 skill coverage matrix`
- `009212d534e1e238fbdbef1120c06292447f33a9` — `feat: add v0.2 diagnostic umbrellas`
- `1da2b651addf4a7d83fd92be6885f2959741318f` — `feat: add EMH skin and canonical voice`
- `c39d1929590c97cea43b03af5abffc99931dd8e5` — `docs: record v0.2 skin acceptance`
- `b9ee7cacc7a644f3638966a1b51494885261421f` — `docs: record disposable skin update acceptance`
- `a100f50d702c9c173a5bbb3eb4e7778698a6f058` — `docs: add EMH concept artwork`

### README concept artwork candidate

- Added the supplied sanitized EMH concept artwork at `docs/assets/emh-concept-art.png` with an exact audited SHA-256 contract, repository inventory coverage, and a centered fan-inspired/unofficial/unaffiliated caption; the existing legal disclaimer remains unchanged.
- TDD evidence: initial focused RED `4 failed, 4 passed, 38 deselected`; initial focused GREEN `8 passed, 38 deselected`; controller repair RED `2 failed, 46 deselected`; repair GREEN `8 passed, 40 deselected` without the external staging file; final full suite `153 passed`; direct public-safety test `48 passed`; and `git diff --check` passed. Direct `scan_bytes` remains strictly fail-closed, while only repository inventory scanning recognizes the exact audited media contract.

### Final local acceptance — 2026-08-08

- Independent specification review: **PASS**, with no HIGH or MEDIUM blockers and no candidate drift.
- Independent quality/security review: **CLEARED**, with no HIGH or MEDIUM blockers; every changed path was reviewed and all four new product skills earned **A (100/100)** under the `skill-auditor` rubric.
- Controller gates: focused v0.2/isolation tests `10 passed`, full suite `153 passed`, direct public-safety scan `0 findings`, every repository script compiled, script modes remained exactly `755`, `git diff --check` passed, and the scoped live-static fingerprint was identical before and after the final suite.
- Exact-archive disposable acceptance at `a100f50d702c9c173a5bbb3eb4e7778698a6f058`: install/update/delete passed; all 12 skills and the skin were discoverable; 21 distribution-owned files were byte-verified; tampered owned files were restored; user config, environment, memory, and session probes were preserved; all nine real `collect_vitals` probes succeeded; output passed the private-identifier scan; and the live-static fingerprint was identical before and after.
- Added exactly one separate FRIDAY-local `emh-orchestration` router outside this repository; it earned **A (93/100)** and a fresh default-profile session discovered and loaded it without installing EMH or mutating live configuration.

### Current acceptance state

EMH v0.2 is accepted as a clean local distribution candidate. Product implementation, independent reviews, controller gates, exact-archive disposable lifecycle acceptance, and the separate FRIDAY-local routing layer are complete. No remote, push, tag, publication, live EMH installation, or skin activation occurred.
