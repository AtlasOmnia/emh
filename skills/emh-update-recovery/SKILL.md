---
name: emh-update-recovery
description: Use when a Hermes update is being assessed, interrupted, failed, or requires bounded recovery, rollback planning, and post-update verification.
version: 0.2.0
author: Jonathan Rivera
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [diagnostics, updates, recovery, rollback, readiness]
    related_skills: [emh-release-intelligence, emh-environment-diagnostics]
---

# EMH update recovery

## Response presentation

Use the shared [EMH response reference](../emh-triage/references/response-templates.md) for normal answers: lead with **What I found**, **What it means**, **Safest next step**, **Permission needed: Yes/No**, then **Technical details**. Preserve this skill's domain workflow, evidence labels, and safety/approval rules; this presentation guidance does not replace them. Keep mutation, external-contact, sensitive-risk, safety, and data-loss warnings in the concise answer, and keep technical proof complete and redacted.

## Overview

This skill assesses and classifies update state; it does not authorize an update. Keep `emh-release-intelligence` read-only and use its offline script before any network or mutation.

Treat an update as ordered stages: source/install identification; readiness; verified backup and rollback prerequisites; mutual-exclusion lock/process check; source acquisition; checkout/package replacement; syntax/startup guard; dependency synchronization; config migration; Desktop rebuild where applicable; gateway/service restart; and post-update verification. Preserve evidence from the first failed stage instead of repeatedly rerunning the updater.

Installed source confirms a cross-process update marker/lock, stage-specific update logic, and guarded recovery paths. Current official docs describe quick/full backup modes, interrupted-terminal protection, post-update checks, and manual rollback, but apply them only to the matching installed version and install method.

Evidence priority is explicit: current runtime and installed source outrank generic guidance. The official docs are authoritative current documentation, but version-match every update or rollback claim. Current entry points are https://hermes-agent.nousresearch.com/docs/getting-started/updating and https://hermes-agent.nousresearch.com/docs/user-guide/configuration.

## When to Use

Use when:

- Deciding whether an update is relevant and whether the installation is ready.
- An update was interrupted, refused, failed, rolled back automatically, or appears half-applied.
- A lock/marker, running process, dirty source summary, dependency failure, config migration, Desktop rebuild, or gateway restart may be the failed stage.
- Installed version/path/method and the executable actually being invoked disagree.
- A verified backup, rollback plan, and post-update validation must be assembled before approval.

**Don't use for:** release comparison alone (use `emh-release-intelligence`); ordinary provider/gateway/tool/interface failures without update correlation; blind “update to fix it” advice; uninstall/reinstall as first-line diagnosis; or destructive recovery without a frozen baseline and operator approval.

## Evidence collection workflow

1. Record **Complaint**; **Vitals**; **Differential diagnosis**; **Confirmed diagnosis**; **Treatment**; **Post-treatment verification**; **Discharge summary or escalation packet**.
2. Freeze the symptom and run `source_status.py --offline`. Record installed version, install method, redacted install-path class, source commit/dirty summary when available, and the executable/version actually invoked.
3. Establish the last known-good version, update trigger/surface, start/end time window, platform, and whether terminal, Desktop, dashboard, gateway, installer, or package manager initiated it.
4. Assess readiness without mutation: supported install method, source availability, free-space evidence supplied by the operator, current process holders, bounded lock-marker metadata, dirty-state summary without filenames, configured backup mode as a non-secret value, and rollback prerequisites.
5. Verify backup evidence before proposing treatment: backup/snapshot type, creation time, source version, readable inventory or integrity check, protected location, and a restoration procedure appropriate to the install method. Existence alone is not a verified backup.
6. Inspect the update marker/lock without deleting it. Record only existence, age, owner PID, PID liveness, and whether the PID belongs to the same update chain. A live lock means wait; a stale-looking marker is a Hypothesis until installed-source rules and process evidence agree.
7. Read only a bounded, local update-log window and preserve the first failing stage. Do not publish raw logs. Classify: preflight/backup; lock/process guard; source fetch/pull/checkout/package; syntax guard/automatic rollback; dependency sync; config migration; Desktop build; gateway/service restart; or validation.
8. Stop before every mutation. Present one bounded treatment with explicit approval, verified backup, rollback command/procedure, abort condition, and post-treatment checks.
9. After an approved update or recovery, verify executable identity/version, source state, `hermes doctor` without `--fix`, config check, original symptom, and gateway/Desktop only if in scope.
10. Label every claim exactly as **Observed**, **Reproduced**, **Confirmed in installed source**, **Officially documented**, **Known upstream fix**, or **Hypothesis**. A newer release is not a Known upstream fix without official version-matched evidence.

## Decision tree

1. **Is this only an update-availability question?**
   - Yes: keep it read-only with offline release intelligence; no update recommendation without symptom/version evidence.
   - No: continue.
2. **Are install method, source identity, last known-good baseline, verified backup, and rollback prerequisites known?**
   - No: HOLD. Gather them before any update, reset, restore, or reinstall.
   - Yes: continue.
3. **Is a live update lock/process present?**
   - Yes: do not start another updater or remove the marker. Wait or escalate with bounded process evidence.
   - No, but marker exists: compare age/PID rules with installed source; cleanup remains approval-gated.
4. **Where is the first failed stage?**
   - Preflight/backup: preserve source and state; repair readiness only.
   - Source fetch/pull/checkout/package: preserve old executable/source and dirty-state summary; do not reset/stash/discard automatically.
   - Syntax guard: determine whether automatic rollback restored the pre-update commit before any retry.
   - Dependency sync: stop; record interpreter/venv/package stage and avoid layering repeated installs onto a half-updated environment.
   - Config migration: keep source/runtime and config-state failures separate; never delete unknown options blindly.
   - Desktop build: separate agent update success from UI artifact failure.
   - Gateway restart: verify updated runtime first, then route service evidence to gateway diagnostics.
5. **Does `hermes --version` still report the old version after apparent success?**
   - Compare executable resolution, install path/method, venv/interpreter, and running long-lived processes. Do not update again until identity is resolved.
6. **Windows reports an executable or venv holder?**
   - Close/stop only the operator-approved holder. Do not bypass `--force` or `--force-venv` as routine recovery.
7. **Did the update succeed but the original symptom remains?**
   - The update was not the confirmed treatment; return to the original domain with version evidence.

## Exact commands and tool calls

These were confirmed in repository scripts, installed help/source, or current official documentation. Run only the smallest relevant subset.

### Read-only allowlist

- `python3 skills/emh-release-intelligence/scripts/source_status.py --offline`
- `hermes --version`
- `hermes version`
- `hermes update --help`
- `hermes status --all`
- `hermes logs list`
- `hermes gateway status`
- `hermes config check`
- `read_file(path="<redacted-update-log-path>", offset=1, limit=200)`

The offline source-status script is the primary assessment and makes no release API call. Treat even bounded logs as private until redacted. `hermes doctor` without `--fix` is reserved for post-update validation after approval because it can perform broader dependency/service checks than this initial allowlist.

### Approval-gated update and recovery actions

- `hermes update --check` performs network access and fetch/comparison work even though current docs state it does not modify working files or restart gateways.
- `hermes update --backup` performs a full backup and update.
- `hermes config migrate` edits configuration interactively.
- `hermes gateway restart` changes service state.
- Manual `git checkout <verified-baseline>` plus dependency synchronization is rollback, not a read-only probe, and is valid only for a confirmed Git install with an exact baseline.
- Marker cleanup, process stop/kill, source reset/stash/restore, snapshot restore, backup restore, dependency reinstall, package replacement, Desktop rebuild, delete, and uninstall all require explicit approval.

Never recommend `hermes update --no-backup`, `--force`, or `--force-venv` as routine recovery. If an exceptional case considers one, document why normal safeguards are false positives, the additional verified backup, rollback, and exact blast radius before seeking separate approval.

## Safety and approval boundaries

**Read-only first.** Never silently update, fetch, pull, checkout, reset, stash, restore, migrate, install, rebuild, restart, stop, kill, delete a marker, replace a venv, uninstall, or roll back.

- Obtain explicit approval immediately before each mutating stage; prior approval to investigate is not approval to update or recover.
- Require a verified backup and install-method-specific rollback before update, reset, restore, dependency replacement, config migration, or service restart.
- Preserve the original source, dirty-state summary, lock/process evidence, and first failing log window. Do not “clean up” evidence before classification.
- Do not expose private paths, remotes, branch names, process arguments, account/profile IDs, credentials, config values, or raw logs.
- Never run two update mechanisms concurrently or bypass a live lock.
- A successful update does not prove the original defect was fixed; repeat the original reproduction.
- Keep `emh-release-intelligence` read-only. Do not convert its release comparison into an updater.

## Common pitfalls and recovery

- **Pitfall: newer means necessary.** Recovery: require an installed-versus-current matrix and official version-matched Known upstream fix for the actual symptom.
- **Pitfall: backup exists, therefore rollback is safe.** Recovery: verify timestamp/source version, readable inventory or integrity, protected location, required tooling, and exact restoration sequence.
- **Pitfall: deleting a stale-looking lock.** Recovery: check age, PID liveness, process ancestry/ownership, and installed-source stale rules; request approval before cleanup.
- **Pitfall: rerunning after a dependency failure.** Recovery: freeze the first error, identify source version versus environment version, and choose rollback or bounded completion instead of stacking installs.
- **Pitfall: source updated but command still old.** Recovery: compare executable resolution, install path/method, venv/interpreter, and long-lived process version before another update.
- **Pitfall: blaming update for a gateway/Desktop-only restart failure.** Recovery: verify core runtime/source first, then classify service or UI artifact separately.
- **Pitfall: using `--force-venv` on Windows.** Recovery: identify and close the approved holder; preserve evidence and escalate if the holder is a false positive.
- **Pitfall: sharing `update.log`.** Recovery: extract only stage, timestamp window, exit status, and the minimal redacted error; keep the raw log private.
- **Pitfall: rollback without config compatibility check.** Recovery: include `hermes config check`, original symptom reproduction, and service/UI validation in the rollback plan.

## Verification checklist

- [ ] Installed version, executable identity, install method, source/dirty summary, platform, and update surface are recorded.
- [ ] Last known-good baseline, verified backup, rollback prerequisites, and abort condition exist before mutation.
- [ ] Lock/marker age, PID liveness, process ownership, and first failed stage are separately classified.
- [ ] Preflight/backup, source, syntax guard, dependency, config, Desktop, gateway, and validation stages are not conflated.
- [ ] Every conclusion has one exact evidence label and adjacent bounded source.
- [ ] No network, update, restart, reset, restore, marker deletion, or install occurred without explicit approval.
- [ ] Post-treatment checks confirm executable/version, source state, config readiness, original symptom, and only the in-scope services/interfaces.
- [ ] Raw logs, credentials, private paths/remotes, and process arguments are absent from shared evidence.

## Escalation packet requirements

Provide a redacted, minimal packet containing:

- **Installed version:** exact Hermes version, executable identity summary, install method, source commit/dirty count when available, and last known-good version.
- **Platform:** OS/version, native/WSL status, update surface, interpreter/venv class, and Desktop/gateway involvement.
- **Reproduction:** update trigger, time window, bounded steps, exit status, and original symptom before/after.
- **Expected behavior:** expected completed stage, version, restart state, and original-symptom result.
- **Actual behavior:** first failed stage, automatic rollback state, current executable/version, and residual runtime state.
- **Minimal evidence:** offline source-status result, backup verification summary, lock age/PID-liveness summary, bounded redacted log excerpt, and installed-source symbol/official URL.
- **Recovery readiness:** verified backup, exact rollback baseline/procedure, required tooling, abort condition, and post-rollback checks.
- **Residual question:** one concrete maintainer question that distinguishes the remaining Hypotheses.
- **Safety record:** every approved mutation, actor/surface, backup/rollback status, residual process/marker/artifact, and post-treatment verification.
- **Redaction boundary:** redact credentials, config values, local paths, remotes, branch names, host/process/profile IDs, endpoints, and private source details. Keep the packet private until reviewed; never attach raw logs, backup contents, full process commands, or unredacted configuration.
