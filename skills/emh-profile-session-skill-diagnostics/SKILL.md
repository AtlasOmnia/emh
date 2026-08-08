---
name: emh-profile-session-skill-diagnostics
description: Use when profile isolation, session context, skill discovery, or tool registration differs across Hermes invocations or platforms.
version: 0.1.0
author: Jonathan Rivera
license: UNLICENSED
platforms: [linux, macos, windows]
---

# EMH profile, session, skill, and tool diagnostics

Keep HERMES_HOME and profile identity explicit. A stored session is not the active context snapshot. Skill discovery/frontmatter/enablement is distinct from tool registration, per-platform enablement, and the fresh-session requirement.

## Workflow

1. Use **Complaint**, **Vitals**, **Differential diagnosis**, **Confirmed diagnosis**, **Treatment**, **Post-treatment verification**, and **Discharge summary or escalation packet** in exactly that order.
2. Inspect active profile, effective HERMES_HOME, and isolation boundaries using redacted summaries. Confirm whether the session is stored, selected, or currently loaded as context.
3. Inspect skill discovery, frontmatter, and enablement separately from tool registration. Check per-platform tool enablement and whether a fresh session is required after a skill/tool change.
4. Compare the same invocation across CLI, TUI, and Desktop only when the profile and home are held constant. Label claims **Observed**, **Reproduced**, **Confirmed in installed source**, **Officially documented**, **Known upstream fix**, or **Hypothesis**.

## Safety boundaries

Do not prune, delete, reset, enable, disable, or rewrite profiles, sessions, skills, or tools without explicit approval. Do not mix profile homes or copy private session content into evidence. A fresh-session check is observational, not permission to discard a session.

## Pitfalls

- Assuming a stored session is the active context.
- Treating discovered frontmatter as enablement.
- Treating tool registration as per-platform availability.
- Comparing surfaces while silently changing HERMES_HOME or profile.

## Verification

- Profile identity and home isolation are explicit.
- Stored session, active snapshot, skill discovery, enablement, and tool registration are separated.
- Platform and fresh-session effects are tested without destructive actions.
- No profile/session/skill/tool lifecycle mutation occurred.

Case record labels: Complaint; Vitals; Differential diagnosis; Confirmed diagnosis; Treatment; Post-treatment verification; Discharge summary or escalation packet.

Evidence labels: Observed; Reproduced; Confirmed in installed source; Officially documented; Known upstream fix; Hypothesis.
