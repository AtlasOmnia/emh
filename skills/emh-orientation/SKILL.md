---
name: emh-orientation
description: Use when the operator starts an EMH session with "setup" or asks to configure optional integrations; walks through consent for the nightly health cron and the repo update-check cron on the default profile.
version: 0.2.0
author: Jonathan Rivera
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [onboarding, orientation, setup, consent, cron, default-profile]
    related_skills: [emh-nightly-self-check, emh-release-intelligence, emh-triage]
---

# EMH orientation

## Overview

Orientation is the first-run consent flow for EMH's optional integrations:

1. **Nightly health cron** (`emh-nightly-self-check`) — a daily 03:00 read-only health sweep that reports `All clear.` or a short `ATTENTION NEEDED` list.
2. **Repo update-check cron** (`emh-repo-update-check`) — a weekly read-only check that compares the installed distribution against its recorded source and reports when an update is available. It never applies updates.
3. **Rescue media** (`emh-rescue-media`) — not a cron: a one-time guided build of a USB rescue kit (redacted baseline, stdlib-only break-glass collector, encrypted patient snapshot). Orientation explains it, records consent, and hands off to the rescue-media skill for the build.

The two crons are registered on the **operator's default profile**, not on the EMH profile, because delivery channels (Telegram, Discord, and similar) belong to the profile that owns the job, and profiles do not inherit each other's channels. current runtime and installed source outrank generic guidance; the official docs are authoritative current documentation, but qualify claims against the installed Hermes version, platform, and configured surface. Nothing is registered, built, changed, or updated without the operator's explicit consent, and each consent is recorded before any mutation.

## When to Use

Use when:

- The operator starts a session with `setup` (the canonical orientation trigger) or asks for orientation.
- The operator asks what the nightly health check is or whether EMH "checks for updates."
- The operator asks about rescue media, a rescue USB, or recovering a machine that cannot start Hermes.
- The operator wants to install or re-configure the optional crons on their default profile, or wants to build rescue media.
- A first-run check is needed to verify the operator's setup state before offering integrations.

**Don't use for:** triage of a reported Hermes failure (use `emh-triage`); diagnosing a broken gateway or channel (use `emh-gateway-diagnostics`); release/version comparison (use `emh-release-intelligence`); update readiness or rollback planning (use `emh-update-recovery`); running the nightly sweep itself (use `emh-nightly-self-check`); building or refreshing rescue media (use `emh-rescue-media` — orientation only explains and consents, then hands off); or any request to apply an update — orientation only checks and reports, and update application is a separate explicit action.

## Evidence collection workflow

Follow the standard case structure — Complaint (the operator's goal, usually "set me up"), Vitals (read-only setup state), Differential diagnosis (why the default profile is the correct home for these crons), Confirmed diagnosis (the operator's explicit consent), Treatment (registration of the chosen crons), Post-treatment verification (re-check the cron inventory), and Discharge summary or escalation packet (what was installed, what was declined, and residual caveats). Label every claim exactly as **Observed**, **Reproduced**, **Confirmed in installed source**, **Officially documented**, **Known upstream fix**, or **Hypothesis**.

1. **Inventory the operator's setup state (read-only, before any offer).**
   - Confirm the EMH profile is installed and identify its recorded source: `hermes profile info emh`.
   - List existing crons on the default profile: `hermes cron list` (no `--profile` flag — the default home is the target).
   - Detect available delivery channels on the default profile: `hermes gateway status` and the default `config.yaml` platform section. A channel present and enabled (for example Telegram) means a notified cron can deliver; absent channels mean `deliver: local` with an explicit warning.
   - Check whether the recorded source has a remote: `git -C <recorded-source> remote -v`. No remote means the update-check cron cannot fetch and must not be registered.
2. **Explain the nightly health cron.** Summarize what it checks (core health, session lifecycle, retention, memory, storage, cron fleet), when it runs (daily 03:00), what it reports (`All clear.` or `ATTENTION NEEDED`, max 10 bullets), and that it is read-only — it never repairs. State the delivery plan based on the detected channels.
3. **Ask for consent to register the nightly health cron on the default profile.** Only the explicit, specific consent covers registration; do not proceed on a general "sure, set things up."
4. **Explain how updating works.** Lay out the update model plainly before offering the check:
   - **What updates:** the distribution-owned files — `SOUL.md`, `skills/`, `skins/` — from the recorded source. Operator-owned state — memories, sessions, credentials, provider keys, logs, configuration — is never touched by an update.
   - **How EMH knows an update exists:** a weekly check compares the installed distribution version against the recorded source's latest commit, reads the CHANGELOG delta, and reports (read-only) whether an update is available and what changed. It never applies anything.
   - **How an update gets applied:** the operator runs `hermes profile update emh` from the recorded source — optionally after `hermes backup` — then verifies with `hermes profile info emh`. EMH never updates itself; applying is always an explicit operator action.
   - **Availability:** the check only works when the recorded source has a remote (for example a GitHub clone). If the source has no remote, say so and skip the offer.
5. **Ask for consent to register the update-check cron.** Record the answer even when declined.
6. **Explain rescue media.** Summarize what it is (a portable USB kit: redacted baseline, break-glass collector that runs even when Hermes cannot, encrypted patient snapshot), what it is not (a bootable OS rescue disk), and its key rule (the snapshot key is held off-media, never on the USB). Ask whether to build it now or defer; a "yes" hands off to `emh-rescue-media` — orientation never duplicates the build.
7. **Register the chosen crons (approval-gated mutations), each followed by verification.** Register from the default-profile context (see Exact commands) so the jobs land in the default store with access to its channels.
8. **Re-check the default cron inventory** and confirm each registered job's name, schedule, deliver target, toolsets, and prompt fingerprint. Report what was installed, what was declined (including rescue media consent), and the residual caveats (for example a `local`-only deliver when no channel was detected).

## Decision tree

1. **Is the default profile reachable from this machine?** — No: stop; report the blocker; do not register anything. Yes: continue.
2. **Does the default profile have a usable delivery channel?** — Yes: plan `deliver` to that channel. No: plan `deliver: local` and warn that notifications require manually checking the default profile's `cron/output/` directory.
3. **Is the nightly health cron already present in the default store?** — Yes: offer to keep, skip, or replace it (never duplicate). No: offer registration.
4. **Does the recorded source have a remote?** — No: skip the update-check offer and say why. Yes: offer registration.
5. **Does the operator want rescue media?** — Yes: explain it (portable kit, not bootable; key off-media), record consent, and hand off to `emh-rescue-media`. No: record the decline and move on.
6. **Did the operator consent to this specific integration?** — No: record the decline and move on. Yes: register, then verify.
7. **Did registration verify cleanly?** — No: do not claim success; escalate with the evidence. Yes: report and close.

## Exact commands and tool calls

Run only the smallest relevant subset. **Profile scoping is the critical detail: the CLI without `--profile` targets the DEFAULT home; `--profile emh` targets the EMH profile's store. These crons must be registered in the default store.**

### Read-only allowlist

- `hermes profile info emh`
- `hermes cron list`
- `hermes gateway status`
- `hermes --version`
- `git -C "<recorded-source>" remote -v`
- `git -C "<recorded-source>" ls-remote --heads origin` (update-check preflight; only when a remote exists)
- `read_file(path="$HERMES_HOME/config.yaml", offset=1, limit=200)` (channel detection; redact any secrets)

### Approval-gated reproductions and mutations

Registration is a mutation and requires the operator's explicit consent for that specific cron. Use the default-profile context:

- `hermes cron create --name emh-nightly-self-check --schedule "0 3 * * *" --prompt-file "<canonical prompt>"` — the canonical prompt is the six-domain contract from `emh-nightly-self-check` with `$HERMES_HOME` substituted to the operator's actual home. Verify the exact flags with `hermes cron create --help` before use; never invent flags.
- `hermes cron create --name emh-repo-update-check --schedule "0 4 * * 1" --prompt-file "<update-check prompt>"` — the prompt is the read-only comparison contract (installed distribution version vs recorded-source HEAD, CHANGELOG delta summary, `Never apply updates.`).
- Deliver target: the detected default-profile channel (for example `--deliver telegram`), or `--deliver local` with the explicit warning when no channel exists.
- Enable toolsets `terminal, file` on both jobs; keep the health job's model cost-effective.

Every mutation requires explicit approval, a verified backup when reversal is difficult, a rollback procedure (remove the job via `hermes cron remove <job-id>`), and post-change verification. Rescue media is **not** a cron: consent hands off to `emh-rescue-media`, which owns the USB build, the key ceremony, and the snapshot. Never silently: register crons, change an existing job, apply updates, build rescue media, touch another profile's store, or edit the EMH distribution files.

## Safety and approval boundaries

Read-only first. Never silently:

- registers, edits, or removes crons on any profile;
- applies distribution updates or changes the installed EMH version;
- touches credentials, auth state, or channel configuration;
- edits SOUL.md, skills, skins, or the distribution manifest;
- runs destructive Git commands or publishes anything.

Before any mutating treatment, require the user's explicit approval, the exact target, an incumbent-writer check, a verified backup when reversal is difficult, a rollback procedure, and a post-change verification command. Approval to orient is not approval to update. Never request or reproduce raw API keys, passwords, cookies, OAuth material, private URLs, full `.env` files, or copied raw logs; prefer status, field names, redacted snippets, hashes, and bounded summaries.

## Common pitfalls and recovery

1. **Registering into the wrong profile store.** A session running in the EMH profile can still execute the default-context CLI; omitting `--profile` targets the default home, and including it targets the EMH store. Always verify afterward with `hermes cron list` (no `--profile`).
2. **Delivering to a channel-less profile.** A job registered in a profile without channels silently produces no notification. Detect channels first; if none exist, register with `deliver: local` and say the operator must check the output directory.
3. **Registering the update-check without a remote.** The check cannot fetch without a remote on the recorded source. Detect it first; do not register the job or promise updates.
4. **Duplicate crons on re-run.** Orientation may run more than once. Check the existing inventory before offering; offer keep/skip/replace instead of duplicating.
5. **Promising updates orientation cannot apply.** Orientation only registers a check. Say plainly that applying an update is a separate explicit action (`hermes profile update emh` from the recorded source, with the operator's review).
6. **Silent consent assumed.** A general "set me up" is not consent for each integration. Ask for each one specifically and record the answer.

## Verification checklist

- [ ] Setup state was inventoried read-only before any offer (profile, default cron store, channels, source remote).
- [ ] Each integration was explained, then consent asked and recorded individually (including rescue media, when offered).
- [ ] Registered jobs landed in the **default** store (verified with `hermes cron list` without `--profile`).
- [ ] Schedules, toolsets, and deliver targets match what was consented to; `deliver: local` cases carry an explicit warning.
- [ ] Update-check was registered only when the recorded source has a remote.
- [ ] Rescue media consent recorded; the build itself, when consented, was handed off to `emh-rescue-media` and not duplicated here.
- [ ] No job was created, changed, or removed without consent; no update was applied; no media was built here.
- [ ] Discharge summary states what was installed, what was declined, and residual caveats.

## Escalation packet requirements

If registration fails, a channel is broken, or the operator reports unexpected behavior, escalate with a redacted packet containing: installed version of Hermes and the EMH distribution version; platform and execution backend; reproduction steps and whether a fresh process reproduces it; expected behavior versus actual behavior; minimal evidence (command names, exit codes, short sanitized findings from the cron inventory and gateway status); residual question and the next read-only discriminator; **Consent status:** which integrations were offered, consented, and registered, declined, or handed off (nightly health cron, update-check cron, rescue media build). Redact keys, tokens, cookies, private URLs, and comparable identifiers; never attach raw logs unless the operator explicitly approves a reviewed packet. Route to `emh-triage` for classification or to `emh-gateway-diagnostics` when the failure is channel delivery.
