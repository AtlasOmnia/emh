---
name: emh-profile-session-skill-diagnostics
description: Use when profile isolation, session context, skill discovery, or tool registration differs across Hermes invocations or platforms.
version: 0.2.0
author: Jonathan Rivera
license: UNLICENSED
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [diagnostics, profiles, sessions, skills, isolation]
    related_skills: [emh-memory-diagnostics, emh-tool-runtime-diagnostics]
---

# EMH profile, session, skill, and tool diagnostics

## Overview

Keep profile identity, `HERMES_HOME`, isolation, stored sessions, active context snapshots, skill discovery/frontmatter/enablement, and tool registration as separate layers. A stored session is not the active context snapshot. A discovered skill is not necessarily enabled, and tool registration is not proof of per-platform availability or model exposure.

Evidence priority is explicit: current runtime and installed source outrank generic guidance. The official docs are authoritative current documentation, but qualify profile, session, skill, and tool claims against the installed Hermes version and the selected home/profile.

## When to Use

Use when:

- Profile isolation or `HERMES_HOME` differs across Hermes invocations, surfaces, or platforms.
- A stored session, active snapshot, fresh session, or resumed session contains different context.
- Skill discovery, frontmatter, enablement, or fresh-session loading differs from expectation.
- Tool registration or per-platform enablement differs even though the same profile and skill appear present.

**Don't use for:** memory persistence without a profile/session boundary; tool dispatch failures after schema exposure; provider, gateway, Kanban, plugin, interface, environment/backend, or update failures without isolation/context evidence. Preserve the profile/session/skill boundary and route the first divergent runtime stage to the owning domain skill.

## Evidence collection workflow

1. Record **Complaint**; **Vitals**; **Differential diagnosis**; **Confirmed diagnosis**; **Treatment**; **Post-treatment verification**; **Discharge summary or escalation packet** in that order.
2. Capture installed version, platform, invocation surface, active profile, effective `HERMES_HOME` summary, working-directory class, and fresh/resumed session state. Redact private paths and identifiers.
3. Confirm profile identity and isolation before comparing any other layer. `hermes profile list`, `show`, and `info` describe different profile facts.
4. Distinguish stored session inventory from the active session and from the session-start context snapshot. Session statistics do not prove loaded context.
5. Inspect skill discovery and frontmatter separately from enablement. A skill file can exist while a profile or fresh session does not load it.
6. Inspect tool registration and per-platform toolset resolution separately from skill discovery. Registration does not prove CLI/TUI/Desktop or model-visible exposure.
7. Compare the same invocation only with profile, home, platform, provider/model, toolsets, and session identity held constant. Fresh-session launch may create state and requires approval.
8. Label every claim exactly as **Observed**, **Reproduced**, **Confirmed in installed source**, **Officially documented**, **Known upstream fix**, or **Hypothesis**.

## Decision tree

1. **Is the active profile and `HERMES_HOME` identity the intended one?**
   - No: classify isolation/context state; do not copy or delete profile data.
   - Yes: continue.
2. **Is the session stored, active, resumed, or a fresh context snapshot?**
   - Unclear: use session statistics and bounded profile evidence; do not infer loaded context.
   - Known: continue.
3. **Is the skill discovered with valid frontmatter?**
   - No: classify file/source/discovery evidence; do not rewrite it as a probe.
   - Yes: continue.
4. **Is the skill enabled in the selected profile and fresh session?**
   - No: classify enablement/session age; do not delete the session.
   - Yes: continue.
5. **Is the tool registered and enabled for the platform?**
   - No: classify registration versus per-platform toolset resolution and route dispatch issues to `emh-tool-runtime-diagnostics`.
   - Yes: continue.
6. **Would the next probe change profile, session, skill, or tool state?**
   - Yes: stop for explicit approval, verified backup, rollback, and post-change verification.
   - No: collect the smallest remaining read-only fact.

## Exact commands and tool calls

These commands were checked against current Hermes help/source. Run only the smallest relevant subset; profile/session metadata and named artifacts remain private until redacted.

### Read-only allowlist

- `hermes --version`
- `hermes status --all`
- `hermes profile list`
- `hermes profile show <profile-name>`
- `hermes profile info <profile-name>`
- `hermes sessions stats`
- `hermes tools list --platform cli`
- `read_file(path="<named-non-secret-skill-artifact>")`

The profile commands require a named profile. The `read_file` path must be a named, non-secret artifact supplied by the operator; do not scan a profile home, session database, credentials, or skill tree broadly.

### Approval-gated reproductions and mutations

- `hermes profile use`, create/delete/rename/import/export/install/update, and profile configuration changes mutate profile state.
- Session browse/resume, fresh session launch, delete/prune/archive/repair/recover, and context export mutate or expose session state.
- Skill enable/disable, file edits, tool enable/disable, plugin/MCP changes, and profile/home switching change discovery or runtime exposure.

Every proposed action requires explicit approval, a verified backup of the affected profile/session/config state, a rollback procedure, abort condition, and post-change verification. No autonomous repair is permitted.

## Safety and approval boundaries

**Read-only first.** Never silently switch profile/home, create/delete/prune/export/repair a session, rewrite a skill, enable/disable a skill or tool, change platform toolsets, or alter credentials/configuration.

- Obtain explicit approval before any fresh/resumed session launch that can create state, any private artifact read, and every mutation.
- Require a verified backup and credible rollback before changing profile, session, skill, tool, plugin, MCP, or configuration state.
- Do not mix homes, profiles, platforms, working directories, providers/models, or session identities while comparing behavior.
- Redact profile/session/tool IDs, paths, prompts, message content, credentials, private URLs, schemas with private defaults, and raw logs. Keep evidence private.
- A fresh session is a diagnostic comparison, not permission to delete the old session. A denial or stale schema is evidence; never silently retry through another profile.
- After an approved change, verify discovery, enablement, tool exposure, profile/home isolation, and the original symptom in the same intended surface.

## Common pitfalls and recovery

- **Pitfall: stored session equals active context.** Recovery: record stored, active, resumed, and snapshot states separately.
- **Pitfall: discovered frontmatter equals enablement.** Recovery: classify discovery, frontmatter, profile enablement, and fresh-session load independently.
- **Pitfall: registration equals platform availability.** Recovery: compare registered tools with platform toolset resolution and current session exposure.
- **Pitfall: comparing while silently changing `HERMES_HOME`.** Recovery: capture redacted home/profile identity on every surface before comparison.
- **Pitfall: deleting a session to test freshness.** Recovery: preserve it and obtain approval for an isolated fresh-session comparison.
- **Pitfall: sharing private session or skill artifacts.** Recovery: retain only the named structural fact or redacted excerpt needed for the diagnosis.

## Verification checklist

- [ ] Installed version, platform, surface, profile, `HERMES_HOME`, working-directory class, and session state are recorded.
- [ ] Isolation/context state, stored session, active snapshot, skill discovery/frontmatter, enablement, registration, and platform exposure are separate.
- [ ] Profile/home/provider/model/toolset/session identity stayed constant during comparison.
- [ ] Every conclusion has one exact evidence label and adjacent bounded source.
- [ ] No profile, session, skill, tool, plugin, MCP, credential, or configuration mutation occurred without approval.
- [ ] Any approved action has a verified backup, rollback, and post-change verification in the same intended surface.
- [ ] Private content, IDs, paths, credentials, schemas, and raw logs are absent from shared evidence.
- [ ] Residual uncertainty is a falsifiable isolation/context question.

## Escalation packet requirements

Provide a redacted, minimal packet containing:

- **Installed version:** exact Hermes version and install method if known.
- **Platform:** OS/version, invocation surface, active profile/home summary, platform toolset, and execution backend.
- **Reproduction:** bounded profile/session/skill/tool commands, fresh/resumed state, working-directory class, and controlled comparison identity.
- **Expected behavior:** expected profile isolation, session context, skill discovery/enablement, and platform tool exposure.
- **Actual behavior:** first divergent isolation/context state and structured status/error.
- **Minimal evidence:** version/status, profile list/show/info summary, session stats, tool list, named artifact fact, and installed-source or official URL.
- **Isolation/context state:** profile/home identity, stored versus active session, snapshot age, skill discovery/frontmatter/enablement, tool registration, and per-platform/fresh-session exposure.
- **Residual question:** one concrete maintainer question that distinguishes the remaining Hypothesis.
- **Safety record:** read-only probes, explicit approvals, side effects, verified backup, rollback, and post-change verification.
- **Redaction boundary:** redact prompts, message/session/profile/tool IDs, paths, credentials, private URLs, private artifact content, and raw logs; keep the packet private until reviewed.
