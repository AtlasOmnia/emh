# Changelog

These are the public weekly release notes for EMH. The newest entries are public release notes for the current candidate. New work is collected under `Unreleased`; at the weekly cut, move completed entries into the next dated version heading. This history is preserved, and a release-note entry does not itself publish, install, or activate anything.

## Unreleased

### Convention

- Keep unreleased changes here until the weekly release-note cut; retain the full historical record below.

### Changed

- Corrected the public repository name and canonical source URLs to `AtlasOmnia/EMH-A-Hermes-Diagnostic-Profile`; historical release-note prose retains the former locator where it describes prior repository state.

## 0.2.9 — 2026-08-14

### Changed

- Made the concise response order canonical across EMH: **What I found**, **What it means**, **Safest next step**, **Permission needed: Yes/No**, then **Technical details**.
- Kept the seven-stage clinical case structure as internal/support detail, while keeping safety, evidence, redaction, and approval rules primary.
- Added an obvious public Start here path and consistent safe-read-only, ask-before-change guidance to the README and user guide.

## 0.2.8 candidate — 2026-08-09

### Changed

- Renamed the GitHub repository's visible name from `emh` to `EMH`; canonical clone, upstream-probe, and public-safety URLs now use `AtlasOmnia/EMH`.
- Preserved the lowercase Hermes machine identifier (`name: emh`) and all `emh-*` skill IDs for install and discovery compatibility.

## 0.2.7 candidate — 2026-08-09

### Added

- Added `emh-reddit-json` (0.2.0), a read-only public Reddit JSON workflow modeled on Donna's proven reading path: bounded listing/search/thread/comment/rules endpoints, `old.reddit.com` and browser fallback guidance, JSON-shape handling, evidence labels, redaction, and explicit exclusion of OAuth, cookies, posting, voting, moderation, and anti-bot bypasses.
- Public-safety URL validation now admits only the bounded public JSON endpoint families used by `emh-reddit-json`, with a restricted query-key allowlist.

### Changed

- Distribution inventory advanced to sixteen class-level skills (fourteen at 0.2.0, two untouched at 0.1.0); manifest and README updated to `0.2.7`.

## 0.2.6 candidate — 2026-08-08

### Added

- `emh-triage` gained the **upstream knowledge fallback**: when local evidence runs out, a read-only probe (`scripts/upstream_check.py`, stdlib-only) compares the installed distribution version against the published GitHub repo and can fetch the relevant subsystem files as labeled **upstream vX — not installed** context (Hypothesis-class). The fallback never installs, updates, git-fetches, or writes; applying an update stays a separate approved action.
- Public-safety gate now allows the distribution's own `raw.githubusercontent.com/AtlasOmnia/EMH` family.

### Changed

- Distribution version advanced to `0.2.6`; no skill contract changed.

## 0.2.5 candidate — 2026-08-08

### Changed

- `emh-orientation` now explains the full update model during `setup`: what updates (distribution-owned files only, never operator state), how EMH detects updates (weekly read-only version comparison + CHANGELOG delta), how updates are applied (`hermes profile update emh` — always an explicit operator action, never self-updating), and the remote-availability gate for the check.
- Distribution version advanced to `0.2.5`; no skill contract changed.

## 0.2.4 candidate — 2026-08-08

### History note

- 2026-08-08: repository history rewritten for publication readiness — all commits re-authored as `AtlasOmnia <110573478+AtlasOmnia@users.noreply.github.com>`; the v0.1 planning doc's private path was scrubbed to a placeholder. SHA references in earlier entries refer to the pre-rewrite history.

### Changed

- `emh-orientation` now explains rescue media as a third optional offering (not a cron): consent is recorded and the build hands off to `emh-rescue-media`; decision tree, workflow, verification, and consent-status fields updated.
- User guide (`docs/user-guide.md`) gained a plain-language Rescue media section; README purpose line covers rescue media.
- Distribution version advanced to `0.2.4`; no skill contract changed.

## 0.2.3 candidate — 2026-08-08

### Added

- Added `emh-rescue-media` (0.2.0), the USB rescue-media skill: redacted machine baseline, stdlib-only break-glass collector (`scripts/breakglass_collect.py`, no Hermes imports — runs when Hermes cannot), two-layer media (plaintext rescue environment vs encrypted patient snapshot with an off-media passphrase-derived key), scope-chosen snapshots, mandatory refresh-and-test hygiene, and the collector-first narrowest-repair deploy sequence. Portable media only — a bootable OS rescue disk remains explicitly out of scope.
- Distribution inventory advanced to fifteen class-level skills (thirteen at 0.2.0, two untouched at 0.1.0); manifest and README updated to `0.2.3`.

### Changed

- Distribution version advanced to `0.2.3`; no existing skill contract changed.

## 0.2.2 candidate — 2026-08-08

### Added

- Added `emh-orientation` (0.2.0), the first-run consent flow: triggered by starting a session with `setup`, it inventories the operator's setup state read-only (default cron store, delivery channels, source remote), explains the optional nightly health cron and repo update-check, asks for consent per integration, and registers chosen crons on the operator's default profile where delivery channels live. The update-check is read-only and never applies updates.
- SOUL.md now directs a `setup` session to run `emh-orientation` before anything else; README install guidance mentions the `setup` trigger.
- Distribution inventory advanced to fourteen class-level skills (twelve at 0.2.0, two untouched at 0.1.0); manifest and README updated to `0.2.2`.

### Changed

- Distribution version advanced to `0.2.2`; no existing skill contract changed.

## 0.2.1 candidate — 2026-08-08

### Added

- Added `emh-nightly-self-check` (0.2.0), the portable contract behind the canonical daily 03:00 read-only Hermes health sweep: core health, session lifecycle, retention, memory, storage, and cron-fleet checks with the `All clear.` / `ATTENTION NEEDED` output contract, read-only allowlist, and cron registration guidance.
- Distribution inventory advanced to thirteen class-level skills (eleven at 0.2.0, two untouched at 0.1.0); manifest and README updated to `0.2.1`.

### Changed

- Distribution version advanced to `0.2.1`; no v0.2 skill contract changed.

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
