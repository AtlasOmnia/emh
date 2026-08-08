---
name: emh-rescue-media
description: Use when building, refreshing, or deploying USB rescue media for a Hermes installation; redacted baseline, stdlib-only break-glass collector, encrypted patient snapshot, narrowest-repair recovery.
version: 0.2.0
author: Jonathan Rivera
license: UNLICENSED
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [rescue, usb, backup, snapshot, recovery, break-glass, encryption]
    related_skills: [emh-update-recovery, emh-triage, emh-release-intelligence, emh-environment-diagnostics]
---

# EMH rescue media

## Overview

Rescue media is a portable USB artifact for recovering a Hermes installation that cannot start normally. It contains: a redacted machine baseline, a **stdlib-only break-glass collector** (no Hermes imports — it runs even when Hermes cannot), offline documentation and recovery instructions, checksums and a backup manifest, and an **encrypted patient snapshot** (optional, scope-chosen). It is portable media, not a bootable operating-system rescue disk; a genuinely bootable USB that recovers a completely broken OS requires separate platform-specific OS images and launchers.

Two layers, never mixed: the **rescue environment** (EMH, scripts, documentation — no secrets) and the **encrypted patient snapshot** (configuration, credentials, sessions, memories, skills, gateways, and other selected state — never plaintext on the USB). The snapshot's key is derived from a passphrase the operator holds separately (for example a password manager); a key stored on the media makes the encryption theater and is forbidden. current runtime and installed source outrank generic guidance; the official docs are authoritative current documentation, but qualify claims against the installed Hermes version, platform, and configured surface. Rescue media does not replace checkpoints: checkpoints roll back code/configuration state, while rescue media is an independent diagnostic environment plus recoverable data — the safer path *before* using a checkpoint.

## When to Use

Use when:

- Building first rescue media for a Hermes installation.
- Refreshing existing media after an EMH release, a Hermes major change, or a platform change.
- Deploying during an incident: Hermes will not launch, import, or respond; the host still runs.
- Comparing the damaged installation against a last-known-good baseline before any restoration.
- Taking an encrypted, scope-chosen snapshot of Hermes state for off-host recovery.

**Don't use for:** checkpoint or rollback planning (use `emh-update-recovery`); diagnosing a specific subsystem failure on a working host (use `emh-triage` and the owning domain skill); routine backup (use `hermes backup`); installed-versus-official version comparison (use `emh-release-intelligence`); building a bootable operating-system rescue disk (out of scope — separate platform images and launchers are required); or any recovery that skips the baseline comparison and narrowest-repair sequence.

## Evidence collection workflow

Follow the standard case structure — Complaint (the machine or Hermes failure), Vitals (the redacted baseline), Differential diagnosis (competing failure explanations before any restore), Confirmed diagnosis (after comparison or reproduction), Treatment (the narrowest approved repair), Post-treatment verification (re-run the original symptom check), and Discharge summary or escalation packet. Label every claim exactly as **Observed**, **Reproduced**, **Confirmed in installed source**, **Officially documented**, **Known upstream fix**, or **Hypothesis**.

1. **Capture the machine baseline (read-only, redacted).** Record: OS and architecture; Hermes version and install method; Python/runtime version; Hermes executable and profile-path classes (not literal private paths); disk space and filesystem information; active profile names and basic status; gateway/service/process status; installed EMH version; hardware summary where useful. No API keys, tokens, cookies, raw logs, or private memory. The break-glass collector emits this JSON without importing Hermes.
2. **Build the rescue media.** Stage on the USB: the EMH distribution (skills, SOUL.md, docs, scripts); the stdlib-only break-glass collector; offline recovery instructions; the machine baseline manifest; checksums of every staged file; and the backup manifest. Add the encrypted patient snapshot only when the operator chooses a scope and completes the key ceremony.
3. **Back up Hermes safely — two layers.** Rescue environment: EMH, scripts, documentation, baseline — no secrets, plaintext is fine. Patient snapshot: selected Hermes state, encrypted with a passphrase-derived key held off-media. Require an explicit scope choice — full backup, profile-only, or configuration-only — never silently copy the entire Hermes home. Never write the patient layer as plaintext.
4. **Refresh and test (hygiene).** After each EMH release or Hermes major change, rebuild the media; verify every checksum; then run a real test pass — plug into a scratch machine, run the collector against a disposable home, confirm the manifest reads back. Untested media is a ritual object, not a rescue plan.
5. **Deploy during recovery.** Plug in the USB; run the standalone collector first; launch a known-good Hermes runtime (a fresh install or the existing venv when importable — the USB does not need to bundle one); have EMH inspect the damaged installation and the backup manifest; compare current state with the last-known-good snapshot; propose the narrowest repair or restoration; take a pre-change snapshot; apply one approved change; verify the original Hermes symptom; repeat only if the symptom persists.

## Decision tree

1. **Is this a build/refresh or a deploy?** — Build: follow phases 1-4 (baseline, stage, snapshot with consent, test). Deploy: continue.
2. **Does the host run?** — No: the portable media cannot boot an OS; state the boundary and stop. Yes: continue.
3. **Can the break-glass collector run without Hermes?** — It must: stdlib only, no Hermes imports. If it cannot, the media is not break-glass; fix the collector before trusting it.
4. **Is a patient snapshot requested?** — Yes: require an explicit scope (full/profile-only/config-only) and the key ceremony (passphrase held off-media) before any snapshot write. No: stage the rescue environment only.
5. **Is the media fresh and verified?** — No: refresh after the latest release and re-verify checksums before relying on it. Yes: continue.
6. **During deploy, is a restoration proposed?** — Yes: compare against the last-known-good baseline first; take a pre-change snapshot; apply one approved change; verify the original symptom. No: continue the narrowest read-only diagnosis.

## Exact commands and tool calls

Run only the smallest relevant subset. The break-glass collector is `skills/emh-rescue-media/scripts/breakglass_collect.py` — stdlib-only, portable.

### Read-only allowlist

- `python3 skills/emh-rescue-media/scripts/breakglass_collect.py --out <staged-baseline.json>`
- `python3 skills/emh-rescue-media/scripts/breakglass_collect.py` (stdout)
- `hermes --version`
- `hermes profile info emh`
- `hermes status --all`
- `hermes profile list`
- `shasum -a 256 <staged-file>...` (macOS/Linux) or `certutil -hashfile <staged-file> SHA256` (native Windows)
- `df -h` (macOS/Linux) or `wmic logicaldisk get size,freespace,caption` (native Windows)
- `git -C "<recorded-source>" status --short --branch`

### Approval-gated reproductions and mutations

Staging the USB, writing the encrypted snapshot, and any restoration step require the operator's explicit approval, a verified backup when reversal is difficult, a rollback procedure, and post-change verification. Never silently: copy the Hermes home, write patient data in plaintext, overwrite existing media, restore from a snapshot, or run destructive Git commands. The snapshot encryption command (for example `age -e -r <recipient>` or `openssl enc -aes-256-cbc`) must use a key derived from a passphrase the operator holds off-media; never store the key or passphrase on the USB.

## Safety and approval boundaries

Read-only first. Never silently:

- copies the entire Hermes home or writes patient-layer data in plaintext;
- stores the snapshot key or passphrase on the media;
- overwrites or wipes existing rescue media;
- restores, deletes, migrates, or rewrites live Hermes state;
- installs, updates, or restarts anything on the patient machine;
- runs destructive Git commands, uploads diagnostics, or publishes anything.

Before any mutating treatment, require the user's explicit approval, the exact target, an incumbent-writer check, a verified backup when reversal is difficult, a rollback procedure, and a post-change verification command. Approval to diagnose is not approval to restore. Never request or reproduce raw API keys, passwords, cookies, OAuth material, private URLs, full `.env` files, or copied raw memories/logs; prefer status, field names, redacted snippets, hashes, and bounded summaries.

## Common pitfalls and recovery

1. **Key stored on the media.** Encryption with the key on the same USB is theater. Recover by moving the key to a password manager or other off-media store and re-encrypting the snapshot.
2. **Bundled runtime staleness.** A "known-good" Hermes runtime shipped on the USB goes stale within weeks and needs its own rescue. Recover by treating the collector as the break-glass artifact and using a fresh install or the existing venv as the rescue runtime.
3. **Plaintext patient data.** A rescue environment that accidentally contains credentials, memories, or raw logs. Recover by re-staging the environment layer from the distribution only and re-running the redaction checks.
4. **Untested media.** Media that has never been read back. Recover by running the mandatory test pass on a scratch machine before any real incident.
5. **Snapshot without a scope choice.** Silently copying the entire Hermes home. Recover by stopping, requiring the explicit scope, and re-staging.
6. **Restore before baseline comparison.** Jumping to an old checkpoint without the collector and comparison step. Recover by running the deploy sequence in order — collector first, compare second, narrowest change third.

## Verification checklist

- [ ] Baseline captured read-only and redacted (no keys, tokens, raw logs, private memory).
- [ ] Break-glass collector runs on a scratch machine with no Hermes installed and emits valid JSON.
- [ ] Rescue environment staged with distribution content only — no patient data.
- [ ] Patient snapshot (when present) is encrypted with an off-media passphrase-derived key; no key material on the USB.
- [ ] Every staged file has a checksum and the checksums verify against the backup manifest.
- [ ] Media refreshed after the latest EMH release; test pass documented.
- [ ] During deploy: collector first, last-known-good comparison, pre-change snapshot, one approved change, original symptom re-verified.

## Escalation packet requirements

If the rescue media itself fails, the collector cannot run, the snapshot cannot be decrypted, or recovery stalls, escalate with a redacted packet containing: installed version of Hermes (or "unavailable") and the EMH distribution version on the media; platform and execution backend; reproduction steps and whether a fresh process reproduces it; expected behavior versus actual behavior; minimal evidence (command names, exit codes, short sanitized findings from the collector and checksum verification); residual question and the next read-only discriminator; **Media state:** build/refresh status, checksum verification result, snapshot encryption and key-ceremony status, and which deploy step failed. Redact keys, tokens, cookies, private URLs, and comparable identifiers; never attach raw logs unless the operator explicitly approves a reviewed packet. Route to `emh-triage` for classification or to `emh-update-recovery` when the failure is checkpoint/rollback related.
