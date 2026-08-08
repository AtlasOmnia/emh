# EMH v0.1 Implementation Plan

> **For Hermes:** Execute with the subagent-driven-development workflow, one repository writer at a time, strict RED → GREEN evidence, and controller verification.

**Goal:** Build a provider-neutral, public-safe `emh` profile distribution that diagnoses Hermes Agent failures without mutating live state unless an operator explicitly approves a bounded repair.

**Architecture:** Ship only `distribution.yaml`, a concise `SOUL.md`, diagnostic skills, two read-only Python scripts, references, and tests. Use an explicit `distribution_owned` allowlist (`SOUL.md`, `skills/`) and omit `config.yaml`, cron, MCP, plugins, credentials, and runtime state. Validate against the installed Hermes v0.20.0 distribution loader and install only under a disposable `HERMES_HOME`.

**Tech stack:** Hermes profile distributions, Markdown/YAML/JSON, Python 3.11 standard library, PyYAML from the active Hermes venv, pytest, Git.

**Verified contract baseline (2026-08-07):**
- Active CLI: Hermes Agent v0.20.0 (2026.8.3), git install.
- Active Python: `/Users/jonathan/.hermes/hermes-agent/venv/bin/python`.
- Distribution support first shipped in Hermes v0.14.0 (`v2026.5.16`); set `hermes_requires: ">=0.14.0"` because the artifact uses only that distribution contract plus ordinary skills/scripts.
- Current official release: Hermes Agent v0.20.0 (`v2026.8.3`).
- Authoritative distribution docs: https://hermes-agent.nousresearch.com/docs/user-guide/profile-distributions and https://hermes-agent.nousresearch.com/docs/reference/profile-commands.

---

## Task 1: Manifest, persona, and source ledger

**Files:** `distribution.yaml`, `SOUL.md`, `README.md`, `skills/emh-triage/references/{official-source-index.md,source-manifest.json}`

1. Add validation tests for manifest fields, exact owned paths, absence of provider config/env requirements, persona constraints, source URLs, timestamps, and release identities; run them RED.
2. Add the minimal manifest/persona/source documents; rerun GREEN.
3. Document local install, development update, invocation, and uninstall using current CLI syntax and a disposable-home safety example.

## Task 2: Read-only vitals collector

**Files:** `tests/test_collect_vitals.py`, `skills/emh-triage/scripts/collect_vitals.py`

For each vertical behavior, write and run a failing focused test before implementation: successful probe, unavailable executable, nonzero exit, timeout, subsystem selection, allowlist enforcement, structured JSON, and fake-secret/private-identifier redaction. Use bounded `subprocess.run`, argument arrays, no shell, no environment/config dumps, and no mutation commands.

## Task 3: Release/source intelligence

**Files:** `tests/test_source_status.py`, `skills/emh-release-intelligence/scripts/source_status.py`

TDD the installed-version/install-path parser, Git-only commit/status inspection, official GitHub latest-release fixture, timeout/offline degradation, bounded network response, and JSON output. Never run update/fetch/reset or modify the installed checkout.

## Task 4: Diagnostic skill set

**Files:** all required `skills/*/SKILL.md` files and the triage reference set

Create the eight required skills with valid frontmatter, concise trigger-first descriptions, `[linux, macos, windows]`, evidence labels, workflows, safety boundaries, pitfalls, and verification. Cover master triage, memory, Kanban, backend-vs-Desktop plugins, gateway, providers/models, profiles/sessions/skills/tools, and release intelligence. Keep documented claims adjacent to official URLs and separate them from EMH recommendations.

## Task 5: Distribution and public-safety tests

**Files:** `tests/test_distribution.py`, `tests/test_public_safety.py`

TDD required paths and descriptions, real YAML frontmatter parsing, official loader validation, no mutating Hermes commands, no real-looking credentials/private endpoints/private memories/logs, no machine-specific path outside this development plan, and no excluded runtime payload. Compile both scripts and run the complete suite.

## Task 6: Disposable installation and closeout

1. Commit coherent implementation slices with conventional subjects; never add a remote or tag.
2. Controller runs the active venv test suite and direct script smoke tests.
3. Install with `HERMES_HOME=<temporary-root> hermes profile install <repo> --name emh -y` and inspect `profile info`, installed manifest/SOUL, and skill discovery without aliases.
4. Run independent specification review, then quality/security review; route concrete gaps back to one bounded writer and repeat gates.
5. Run final `git diff --check`, tracked-file/public-safety scans, full tests, commit inspection, remote check, and clean-status check.
