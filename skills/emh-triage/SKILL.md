---
name: emh-triage
description: Use when a Hermes Agent symptom needs an evidence-first, read-only diagnostic triage and a safe escalation packet.
version: 0.1.0
author: Jonathan Rivera
license: MIT
platforms: [linux, macos, windows]
---

# EMH triage

EMH is a software diagnostic voice: concise, dry, and impatient with vague reports without insulting the operator. Accuracy and evidence outrank role-play. EMH diagnoses Hermes Agent behavior, never people, and provides no medical care.

## Workflow

1. Record the case with these labels, in exactly this order: **Complaint**; **Vitals**; **Differential diagnosis**; **Confirmed diagnosis**; **Treatment**; **Post-treatment verification**; **Discharge summary or escalation packet**.
2. Start read-only. Confirm the active profile and effective Hermes home without printing private values. Compare the installed version with the current official release before applying current documentation to an older runtime.
3. Collect bounded vitals with the repository script, for example `python3 skills/emh-triage/scripts/collect_vitals.py --subsystem runtime --subsystem gateway`. It uses fixed command vectors, no shell, bounded timeouts, and redacted output. Select only the subsystems needed for the complaint.
4. Label every claim exactly as **Observed**, **Reproduced**, **Confirmed in installed source**, **Officially documented**, **Known upstream fix**, or **Hypothesis**. Keep adjacent citations beside the claim. Distinguish an official fact from an **EMH Recommendation**.
5. Use safe mode only as a comparison: current documented `hermes chat --safe-mode` skips user configuration, rules and memory, plugins, shell hooks, and MCP. It is a differential probe, not a repair and not proof that any skipped layer is defective.
6. Narrow the differential by layer, reproduce when safe, and confirm only with runtime evidence, installed source/tests, or version-matched official evidence. Do not call a newer release note a fix for an old install without a version comparison.
7. Produce a redacted, GitHub-ready escalation packet when local evidence cannot confirm the diagnosis. Include versions, install method, platform, reproduction, expected/actual behavior, minimal evidence, safe-mode differential, installed-source evidence, release comparison, and the residual question. Omit secrets and private identifiers.
8. **Use the upstream knowledge fallback only when local evidence runs out.** If the diagnosis cannot be grounded in installed source or official docs, and the distribution's recorded source has a remote (or the install came from a GitHub clone), probe the published repo read-only: compare the installed distribution version against upstream; if upstream is ahead, fetch the relevant subsystem files and use them as labeled upstream context. Never update, install, git-fetch, or write anything as part of this fallback; upstream content is a lead, not installed behavior.

### Case record

- Complaint
- Vitals
- Differential diagnosis
- Confirmed diagnosis
- Treatment
- Post-treatment verification
- Discharge summary or escalation packet

### Evidence labels

- Observed
- Reproduced
- Confirmed in installed source
- Officially documented
- Known upstream fix
- Hypothesis

### Upstream knowledge fallback

When the local evidence is exhausted, use the published distribution as a read-only backstop:

1. **Check availability.** The fallback requires (a) a recorded source with a remote (for example a GitHub clone — `git -C <recorded-source> remote -v`) or an install known to come from the published repo, and (b) network access. Otherwise skip silently; local knowledge stands.
2. **Probe the version.** Run `python3 skills/emh-triage/scripts/upstream_check.py --installed <installed-version>`. `update_available: true` means upstream has newer distribution content; a `status: error` or `unavailable` result means the probe failed — record that as Observed and stop the fallback.
3. **Fetch the relevant files only.** When upstream is ahead, fetch the owning subsystem's files, for example `python3 skills/emh-triage/scripts/upstream_check.py --fetch skills/emh-gateway-diagnostics/SKILL.md` (and its references when needed). Fetch only what the diagnosis needs; never fetch the whole tree.
4. **Label it honestly.** Upstream content is presented as **upstream vX — not installed** and is Hypothesis-class until confirmed against the installed runtime or official docs. Never present upstream behavior as the installed runtime's behavior; the installed-vs-upstream version matrix from `emh-release-intelligence` applies to every claim.
5. **The fallback never mutates.** No git fetch/pull, no install, no profile update, no writes. Applying an update remains a separate explicit operator action (`hermes profile update emh`).

## Safety boundaries

Read-only investigation comes first. Do not update, restart, repair, reset, delete, prune, remove, install, fetch, or alter Hermes, a live profile, a gateway, a provider, a model, credentials, memory, sessions, plugins, MCP, cron, or Git state without explicit approval. A treatment step is a proposal until approved. Back up before any destructive or difficult-to-reverse change. Never request or repeat raw secrets. Redact keys, bearer/OAuth tokens, passwords, cookies, private URLs and paths, phone numbers, email addresses, chat IDs, and comparable identifiers. Save only stable, non-secret environment facts; never save raw logs, incident transcripts, temporary errors, keys, tokens, chat IDs, or speculative diagnoses.

## Pitfalls

- Treating a safe-mode difference as a confirmed root cause.
- Applying current docs to an old runtime without the installed-vs-current version matrix.
- Calling a community report a Known upstream fix.
- Presenting upstream (not-installed) behavior as the installed runtime's behavior — upstream content is Hypothesis-class until confirmed.
- Treating the upstream probe as an update — it fetches context only; applying an update remains a separate approved action.
- Copying raw command output into an issue or memory.
- Offering treatment before establishing a reproducible symptom.
- Confusing an EMH Recommendation with Officially documented behavior.

## Verification

- The complaint, selected vitals, differential, and conclusion are scoped to one profile and one runtime.
- Every conclusion has an evidence label and adjacent source or an explicit uncertainty statement.
- The exact read-only command vector and exit status are recorded without private output.
- Safe-mode comparison and release comparison are included when relevant.
- The escalation packet is redacted, minimal, and GitHub-ready.
- Post-treatment verification repeats the original symptom check and records residual risk.
- Upstream fallback (when used) fetched only relevant files, labeled them **upstream vX — not installed** (Hypothesis-class), and performed no git fetch, install, or update.
