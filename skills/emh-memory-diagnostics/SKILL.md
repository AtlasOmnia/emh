---
name: emh-memory-diagnostics
description: Use when Hermes memory appears missing, stale, profile-scoped incorrectly, or dependent on an optional external provider.
version: 0.2.0
author: Jonathan Rivera
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [diagnostics, memory, profiles, providers, sessions]
    related_skills: [emh-provider-diagnostics, emh-profile-session-skill-diagnostics]
---

# EMH memory diagnostics

## Response presentation

Use the shared [EMH response reference](../emh-triage/references/response-templates.md) for normal answers: lead with **What I found**, **What it means**, **Safest next step**, **Permission needed: Yes/No**, then **Technical details**. Preserve this skill's domain workflow, evidence labels, and safety/approval rules; this presentation guidance does not replace them. Keep mutation, external-contact, sensitive-risk, safety, and data-loss warnings in the concise answer, and keep technical proof complete and redacted.

## Overview

Diagnose built-in and external memory as separate systems. Built-in profile-scoped MEMORY.md and USER.md facts, the session-start context snapshot, and an optional external memory provider answer different questions: a fact may be persisted but absent from a stale snapshot, or a provider may be configured without being reachable or authenticated.

Preserve the taxonomy: memory = durable facts/preferences; skills = repeatable procedures.

Use read-only configuration checks for `memory.write_approval` and `skills.write_approval`.

These gates are preventive controls over future built-in writes, not cleanup.

Evidence priority is explicit: current runtime and installed source outrank generic guidance. The official docs are authoritative current documentation, but every documented claim must be qualified against the installed Hermes version and profile. Do not infer data loss from one missing retrieval result.

## Memory write-approval diagnostics

These write-approval gates are preventive controls over future built-in writes, not a cleanup mechanism. Enabling either gate is persistent config mutation requiring explicit approval; do not run it. Explain explicit pending/review/approve/reject behavior for built-in writes without claiming coverage for external memory providers, plugins, or custom writers. Existing consolidation is a separately scoped mutation needing backup, review, rollback, and verification. Preserve the taxonomy: memory = durable facts/preferences; skills = repeatable procedures; skill references = detailed supporting knowledge; project/session documentation = temporary work.

Evidence priority is explicit: current runtime and installed source outrank generic guidance. The official docs are authoritative current documentation, but every documented claim must be qualified against the installed Hermes version and profile. Do not infer data loss from one missing retrieval result.

## When to Use

Use when:

- Built-in memory appears missing, stale, unexpectedly scoped, or different between profiles.
- A session does not contain a fact that appears in MEMORY.md or USER.md, or the session-start context snapshot may be stale.
- An external memory provider is configured and its configured, reachable, authenticated, persisted, or loaded state is unclear.
- A fresh-session comparison is needed to distinguish memory state from profile/session routing.

**Don't use for:** provider endpoint or model failures without a memory symptom; profile or session isolation incidents without a memory-state question; gateway delivery, Kanban queue/worker behavior, plugin lifecycle, tool registration, interface rendering, environment/backend mismatch, or update recovery. Route those cases to the domain skill after preserving only the smallest memory boundary evidence.

## Evidence collection workflow

1. Record **Complaint**; **Vitals**; **Differential diagnosis**; **Confirmed diagnosis**; **Treatment**; **Post-treatment verification**; **Discharge summary or escalation packet** in that order.
2. Capture installed version, platform, active profile, effective `HERMES_HOME` summary, and whether the session is new or resumed. Redact paths and identifiers.
3. Establish the memory boundary: built-in MEMORY.md/USER.md, session-start context snapshot, or external memory provider. Do not combine their states.
4. Use the read-only allowlist below to collect memory status and profile facts. Artifact selection is explicit and limited; read a named artifact only when the operator identifies it as non-secret, and never dump or share private memory contents.
4. For built-in memory, distinguish file presence, readable content, profile scope, and snapshot age. A stale session-start context snapshot is a staleness differential, not proof of deletion.
5. For an external memory provider, report configured, reachable, authenticated, persisted, and loaded as separate states. Reachability does not prove persistence, and persistence does not prove that the current session loaded the fact.
6. For write-approval gates, treat pending/review/approve/reject as built-in write states; do not deduplicate/reconcile existing state or claim coverage for external memory providers, plugins, or custom writers.
7. Compare one controlled fresh session only with explicit approval because launching it may create session or log state. Never delete a session to test loading.
8. Label every claim exactly as **Observed**, **Reproduced**, **Confirmed in installed source**, **Officially documented**, **Known upstream fix**, or **Hypothesis**. Put the source beside the claim.

## Decision tree

1. **Is the built-in memory artifact present and readable in the intended profile scope?**
   - No: classify missing artifact or permission evidence; do not reset or recreate it.
   - Yes: continue.
2. **Does the stored fact exist but the session-start context snapshot omit it?**
   - Yes: classify snapshot staleness, context budgeting, or session routing; do not call it data loss.
   - No: continue.
3. **Is an external provider configured?**
   - No: keep the diagnosis within built-in memory and profile/session boundaries.
   - Yes: classify configured, reachable, authenticated, persisted, and loaded separately.
4. **Does the same fact fail only in one profile or home?**
   - Yes: route the isolation/context differential to `emh-profile-session-skill-diagnostics`.
   - No: continue with memory/provider evidence.
5. **Would the next probe write, reset, delete, export, or create session state?**
   - Yes: stop and present an approval-gated proposal with a verified backup, rollback, and post-change verification.
   - No: collect the smallest remaining read-only fact.

## Exact commands and tool calls

These commands were checked against current Hermes help/source. Run only the smallest relevant subset, and redact output before sharing.

### Read-only allowlist

- `hermes --version`
- `hermes status --all`
- `hermes memory status`
- `hermes profile list`
- `hermes profile show <profile-name>`
- `hermes profile info <profile-name>`
- `read_file(path="<named-non-secret-memory-artifact>", offset=1, limit=200)`

`hermes profile show` and `hermes profile info` require a named profile and may display private configuration metadata; treat output as private. The `read_file` probe is limited to the explicitly named artifact and the bounded first 200 lines. Never dump or share private memory contents; any private artifact read requires explicit approval immediately before reading and redaction before evidence. Do not pass a credential or copy raw memory contents into evidence.

### Approval-gated reproductions and mutations

- Starting a fresh session or invoking a memory-writing path can create session, log, or memory state.
- `hermes memory reset`, `hermes memory off`, provider setup, export, delete, migration, or profile changes are mutations.
- Reading a named non-secret artifact beyond the allowlist is a proposed probe and still requires review when it may contain private memory; any private artifact read requires explicit approval and redaction.

Every proposed action requires explicit approval immediately before execution, a verified backup when state can change, a rollback procedure, abort condition, and post-change verification against the original symptom. Never silently mutate state or continue after an abort condition; no autonomous repair is permitted.

## Safety and approval boundaries

**Read-only first.** Never silently reset, delete, rewrite, export, migrate, prune, disable, or change memory, provider, profile, session, or credentials. Investigation approval is not mutation approval.

- Require explicit approval for any fresh-session launch, external provider contact, memory write, profile change, or data export.
- Before a destructive or difficult-to-reverse action, require a verified backup and a credible rollback procedure; name the exact scope and abort condition.
- Keep raw memory entries, prompts, session transcripts, tokens, cookies, private paths, provider URLs, and raw logs private. Redact identifiers and retain only stable non-secret facts.
- A provider error is not evidence that built-in memory was deleted. A missing snapshot is not permission to reset memory.
- Existing consolidation is a separately scoped mutation needing backup, review, rollback, and verification.
- After an approved change, repeat the original memory reproduction, verify the intended profile/home, and record residual risk. Never silently broaden scope.

## Common pitfalls and recovery

- **Pitfall: treating one missing retrieval as deletion.** Recovery: compare built-in artifact state, profile scope, snapshot age, and provider state separately.
- **Pitfall: calling a configured provider authenticated.** Recovery: classify configured, reachable, authenticated, persisted, and loaded independently.
- **Pitfall: reading a stale session-start context snapshot as current storage.** Recovery: record snapshot age and use an approved fresh-session comparison.
- **Pitfall: mixing profile homes.** Recovery: record a redacted profile and `HERMES_HOME` identity before comparing.
- **Pitfall: resetting memory as a diagnostic shortcut.** Recovery: stop, preserve evidence, propose a verified backup and rollback instead.
- **Pitfall: sharing raw memory or logs.** Recovery: discard the shareable copy and retain a minimal redacted excerpt or boolean result.

## Verification checklist

- [ ] Installed version, platform, profile, `HERMES_HOME` summary, and session age are recorded without private values.
- [ ] Built-in memory, session-start context snapshot, and external provider state are separate.
- [ ] Configured, reachable, authenticated, persisted, and loaded states are not conflated.
- [ ] Every conclusion has one exact evidence label and adjacent source.
- [ ] No reset, deletion, export, provider change, or session mutation occurred without explicit approval.
- [ ] Any approved change has a verified backup, rollback, and post-change reproduction.
- [ ] Raw memory, prompts, credentials, private identifiers, and raw logs are absent from shared evidence.
- [ ] Residual uncertainty is stated as a falsifiable question.

## Escalation packet requirements

Provide a redacted, minimal packet containing:

- **Installed version:** exact Hermes version and install method if known.
- **Platform:** OS/version, active profile/home summary, interface, and fresh/resumed session state.
- **Reproduction:** bounded prompt or read-only command sequence, target profile, memory boundary, and snapshot age.
- **Expected behavior:** whether the fact should be persisted, loaded, or visible in the current snapshot.
- **Actual behavior:** the first divergent memory state and the observed status.
- **Minimal evidence:** status output, profile scope summary, snapshot-age summary, named non-secret artifact result, and installed-source or official URL.
- **Memory state:** built-in artifact, profile scope, snapshot state, external-provider configured/reachable/authenticated state, and persisted/loaded distinction.
- **Residual question:** one concrete maintainer question that distinguishes the remaining Hypothesis.
- **Safety record:** read-only probes, explicit approvals, side effects, verified backup, rollback, and post-change verification.
- **Redaction boundary:** redact credentials, memory contents, prompts, paths, endpoints, account/session/profile IDs, private URLs, and raw logs; keep the packet private until reviewed.
