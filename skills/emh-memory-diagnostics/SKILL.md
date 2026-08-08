---
name: emh-memory-diagnostics
description: Use when Hermes memory appears missing, stale, scoped to the wrong profile, or dependent on an optional provider.
version: 0.1.0
author: Jonathan Rivera
license: UNLICENSED
platforms: [linux, macos, windows]
---

# EMH memory diagnostics

Diagnose memory scope and availability without treating a missing result as proof of data loss. Distinguish built-in profile-scoped MEMORY/USER facts from optional external provider status.

## Workflow

1. Record **Complaint**, **Vitals**, **Differential diagnosis**, **Confirmed diagnosis**, **Treatment**, **Post-treatment verification**, and **Discharge summary or escalation packet** in that order.
2. Identify the active profile and effective Hermes home using a redacted summary. Inspect built-in memory status and distinguish stored facts from the session-start context snapshot and its staleness.
3. If an external memory provider is configured, report configured, reachable, and authenticated as separate states. Provider reachability does not prove that a fact was persisted or loaded.
4. Compare a fresh session-start snapshot with the built-in profile-scoped MEMORY/USER facts. Treat a stale snapshot as a routing or session-context differential, not as permission to reset memory.
5. Label claims **Observed**, **Reproduced**, **Confirmed in installed source**, **Officially documented**, **Known upstream fix**, or **Hypothesis** and cite adjacent sources.

## Safety boundaries

Read-only first. Do not reset, delete, rewrite, export, migrate, or prune memories; change a provider; or request raw credentials without explicit approval. Persist only stable, non-secret environment facts. Never retain raw memory entries, logs, incident transcripts, tokens, cookies, chat IDs, temporary errors, or speculative diagnoses.

## Pitfalls

- Confusing a built-in profile fact with an optional external provider.
- Calling a stale session snapshot data loss.
- Treating provider reachability as successful memory persistence.
- Deleting memory to test whether it reloads.

## Verification

- Active profile/home and snapshot age are recorded without private paths.
- Built-in facts, optional provider status, and session context are separate.
- No reset or deletion was performed.
- The conclusion names the evidence label and remaining uncertainty.

Case record labels: Complaint; Vitals; Differential diagnosis; Confirmed diagnosis; Treatment; Post-treatment verification; Discharge summary or escalation packet.

Evidence labels: Observed; Reproduced; Confirmed in installed source; Officially documented; Known upstream fix; Hypothesis.
