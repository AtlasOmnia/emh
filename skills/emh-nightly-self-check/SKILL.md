---
name: emh-nightly-self-check
description: Use when operating the recurring nightly read-only Hermes health self-check (core health, sessions, retention, memory, storage, cron fleet); detects anomalies without repairing.
version: 0.2.0
author: Jonathan Rivera
license: UNLICENSED
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [health, nightly, self-check, monitoring, read-only, cron-fleet]
    related_skills: [emh-triage, emh-memory-diagnostics, emh-gateway-diagnostics, emh-environment-diagnostics, emh-update-recovery]
---

# EMH nightly self-check

## Overview

The nightly self-check is a bounded, read-only health sweep over the major Hermes persistence and runtime surfaces: core health, session lifecycle, retention, memory, storage, and the cron fleet. It runs on a schedule (canonical deployment: daily at 03:00) and either confirms health or reports a short, evidence-labeled anomaly list.

This skill is the portable contract behind that job. current runtime and installed source outrank generic guidance; the official docs are authoritative current documentation, but qualify claims against the installed Hermes version, platform, and configured surface. The sweep never repairs: no restart, prune, vacuum, consolidation, migration, credential change, or configuration edit.

## When to Use

Use when:

- Running or setting up the recurring nightly Hermes health self-check.
- A scheduled sweep needs a bounded, read-only anomaly report (core, sessions, retention, memory, storage, cron fleet).
- Investigating whether a system looks healthy without touching it.
- A health report must distinguish genuine failures from optional unset integrations or API keys.

**Don't use for:** triage of a specific reported failure (use `emh-triage`); memory-failure diagnosis (use `emh-memory-diagnostics`); gateway outage diagnosis (use `emh-gateway-diagnostics`); environment or backend mismatch (use `emh-environment-diagnostics`); update readiness or rollback planning (use `emh-update-recovery`); repair, restart, prune, vacuum, or consolidation of any kind; or any workflow where read-only collection would delay an approval-gated repair. The self-check classifies and reports; the owning domain skill diagnoses, and treatment is always a separate approval-gated step.

## Evidence collection workflow

Record findings in the standard case structure — Complaint (the anomaly as observed), Vitals (bounded read-only state), Differential diagnosis (competing explanations for a flagged anomaly), Confirmed diagnosis (only after reproduction or corroboration), Treatment (proposal only, never executed here), Post-treatment verification (the exact recheck to run after an approved repair), and Discharge summary or escalation packet (the redacted anomaly list routed to the owning domain).

1. **Core health.** Run `PAGER=cat hermes status` and `PAGER=cat hermes doctor`. Distinguish genuine failures from optional unset integrations/API keys; label each claim exactly as **Observed**, **Reproduced**, **Confirmed in installed source**, **Officially documented**, **Known upstream fix**, or **Hypothesis**.
2. **Session lifecycle.** Query the session store read-only (`$HERMES_HOME/state.db`); `sessions.ended_at IS NULL` means open. Group open sessions by source and age. Flag detached sessions only when stale: cli/api_server/tui/speech-bridge older than 24h; cron/subagent older than 6h. Do not flag long-lived telegram/discord/bluebubbles sessions merely for being open. If detached counts spike, group exact first user messages to identify a runaway producer instead of guessing.
3. **Retention health.** Confirm the configured retention prune script exists and passes a syntax check (`bash -n`). Inspect the latest completed block in the retention log. Flag a missing completion, nonzero failure, or no successful run within 30 hours. Do not run the cleanup.
4. **Memory health.** Measure the built-in memory files (`$HERMES_HOME/memories/MEMORY.md`, `USER.md`) by bytes, non-whitespace characters, and `§` entry count. Run `hermes memory status`; flag a configured provider that is not installed or unavailable. If the Mnemosyne executable exists, run its read-only `stats` command only — never `sleep`, `dream`, or consolidation. Treat built-in and Mnemosyne as separate layers; report exactly which layer is unhealthy.
5. **Storage signal.** Report the state database and WAL sizes plus filesystem free space. Flag WAL above 1 GB, free space below 10 GB, or state-db growth above 25% versus the prior nightly report when a prior value is available. Do not vacuum or delete backups.
6. **Cron fleet health.** Do not infer job health from the aggregate count in `hermes status` or from `hermes doctor` alone. Read the job store and execution database directly and run `PAGER=cat hermes cron status`. For every enabled job, flag `last_status` values of `error` or `blocked_config`, and flag any nonempty `last_error`. Include job name, job ID, last run time, exact error class/root cause, and the recommended next step. Inspect each enabled job's latest execution attempt; flag a latest terminal state of `failed` or `unknown`, and repeated failures when the last two or more attempts failed. Flag enabled jobs whose `next_run_at` is more than 10 minutes overdue when no corresponding execution is currently `claimed` or `running`. Ignore historical errors on paused or disabled jobs. If a failed enabled job uses `deliver: local`, note that it has no proactive user notification route in the current setup.

## Decision tree

1. **Is the anomaly a genuine failure?** — No (optional unset integration, expected state): record as healthy, do not flag. Yes: continue.
2. **Is the anomaly within this sweep's six domains?** — No: preserve only the bounded evidence and route to the owning diagnostic skill. Yes: continue.
3. **Does the evidence support the flag?** — Require Observed or Reproduced state, not Hypothesis alone. No: record as Hypothesis and move on.
4. **Can the next probe stay read-only?** — No: stop for explicit approval; the sweep never mutates. Yes: collect the smallest remaining fact.
5. **Any enabled-job failures or overdue runs?** — Yes: include job name, ID, last run, exact error class, and recommended next step in the report.
6. **Output contract** — If everything is healthy, respond exactly `All clear.` Otherwise start with `ATTENTION NEEDED` and list only actionable anomalies with evidence and recommended next step; maximum 10 bullets.

## Exact commands and tool calls

Run only the smallest relevant subset; output remains private until redacted.

### Read-only allowlist

- `PAGER=cat hermes status`
- `PAGER=cat hermes doctor`
- `hermes memory status`
- `PAGER=cat hermes cron status`
- `~/.hermes/hermes-agent/venv/bin/mnemosyne stats` (read-only stats only; never sleep/dream/consolidation)
- `read_file(path="$HERMES_HOME/state.db", ...)` (read-only SQLite queries only)
- `read_file(path="$HERMES_HOME/memories/MEMORY.md", offset=1, limit=200)`
- `read_file(path="$HERMES_HOME/memories/USER.md", offset=1, limit=200)`
- `read_file(path="$HERMES_HOME/cron/jobs.json", offset=1, limit=2000)`
- `read_file(path="$HERMES_HOME/cron/executions.db", ...)` (read-only queries only)
- `read_file(path="$HERMES_HOME/logs/session-retention-prune.log", offset=1, limit=200)`

### Approval-gated reproductions and mutations

Anything that reproduces by sending real messages, restarts a process, touches credentials, prunes, vacuums, consolidates, migrates, or edits configuration requires explicit approval, a verified backup when reversal is difficult, a rollback procedure, and post-change verification. The nightly sweep normally never reaches this section; if a repair is needed, the owning domain skill owns it.

## Safety and approval boundaries

Read-only first. Never silently:

- repairs, restarts, prunes, vacuums, consolidates memory, or changes configuration;
- sends messages, touches credentials or auth state, or migrates data;
- deletes, edits, or rewrites memories, sessions, skills, logs, or databases;
- runs destructive Git commands, uploads diagnostics, or publishes anything;
- launches overlapping writers against a repository or live profile.

Before any mutating treatment, require the user's explicit approval, the exact target, an incumbent-writer check, a verified backup when reversal is difficult, a rollback procedure, and a post-change verification command. Approval to diagnose is not approval to repair. Never request or reproduce raw API keys, passwords, cookies, OAuth material, private URLs, full `.env` files, or copied raw memories/logs; prefer status, field names, redacted snippets, hashes, and bounded summaries.

## Common pitfalls and recovery

1. **Flagging optional integrations as failures.** Unset API keys and optional adapters are expected in many setups; verify against `hermes status`/`hermes doctor` output before flagging.
2. **Long-lived gateway sessions misread as leaks.** Telegram/discord/bluebubbles sessions are expected to stay open; apply the documented age thresholds per source.
3. **Memory layers conflated.** Built-in MEMORY.md/USER.md and Mnemosyne are separate persistence layers; report exactly which layer is unhealthy.
4. **Running consolidation during a health check.** Never run memory sleep/dream/consolidation or any prune; the sweep reports, the operator repairs under approval.
5. **Cron health inferred from aggregate counts.** Read jobs.json, executions.db, and `hermes cron status` directly; a job can be enabled, erroring, and invisible in a summary count.
6. **Repair implied by report.** `ATTENTION NEEDED` is a classification, not authorization; every repair returns to the explicit approval/backup/rollback gate.

## Verification checklist

- [ ] Every check stayed read-only; no process, database, or configuration was touched.
- [ ] Claims carry evidence labels; Hypothesis never presented as fact.
- [ ] Detached-session flags respect the per-source age thresholds.
- [ ] Retention health judged from the latest completed log block, not absence of errors alone.
- [ ] Cron flags include job name, job ID, last run time, exact error class, and recommended next step.
- [ ] Output contract honored: `All clear.` or `ATTENTION NEEDED` with at most 10 actionable bullets.
- [ ] No raw secrets, tokens, private URLs, or full logs in the report; bounded redacted findings only.

## Escalation packet requirements

When an anomaly exceeds the sweep or needs a repair, escalate with a redacted packet containing: installed version of Hermes; platform and execution backend; reproduction steps and whether a fresh process reproduces it; expected behavior versus actual behavior; minimal evidence (command names, exit codes, short sanitized findings); residual question and the next read-only discriminator; **Health status:** the sweep classification (All clear / ATTENTION NEEDED) and the anomaly domains affected. Redact keys, tokens, cookies, private URLs, and comparable identifiers; never attach raw logs unless the operator explicitly approves a reviewed packet. Route to the owning diagnostic skill for classification or to `emh-triage` when the anomaly crosses domains.

## Cron registration

The canonical deployment registers this skill as a self-contained job (schedule `0 3 * * *`, read-only toolsets `terminal, file`, a cost-effective provider/model, `deliver` to a channel the operator actually reads). The job prompt is the six-domain workflow above plus the output contract; it must not attach repair instructions. Re-register after Hermes updates only when command names or store paths change.
