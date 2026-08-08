---
name: emh-plugin-diagnostics
description: Use when a Hermes backend plugin or Desktop plugin is absent, unexpected, disabled, or behaving differently at runtime.
version: 0.2.0
author: Jonathan Rivera
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [diagnostics, plugins, backend, desktop, registration]
    related_skills: [emh-tool-runtime-diagnostics, emh-interface-diagnostics]
---

# EMH plugin diagnostics

## Overview

Treat backend and Desktop plugins as different plugin surfaces. Python backend plugins have manifest, discovery, registration, enablement, import, requirement, and runtime concerns. Uncompiled JavaScript Desktop plugins have inventory, Desktop settings, hot reload, preload/IPC, and UI reachability concerns. Backend registration does not imply Desktop UI.

Evidence priority is explicit: current runtime and installed source outrank generic guidance. The official docs are authoritative current documentation, but qualify plugin behavior against the installed version, plugin type, and profile/home.

## When to Use

Use when:

- A backend plugin or Desktop plugin is absent, unexpectedly present, disabled, or reported with a lifecycle error.
- Manifest, registration, enablement, import/runtime, inventory/settings, hot reload, or UI reachability disagree.
- A plugin appears in one profile, platform, or surface but not another.
- Plugin behavior may be confused with tool discovery, interface rendering, provider state, or environment/backend isolation.

**Don't use for:** a missing or denied tool without a plugin-surface question; interface rendering alone; provider or gateway failures; profile/session isolation without plugin evidence; memory; Kanban; environment/backend mismatch; or update recovery. Preserve the plugin boundary evidence and route to tool-runtime or interface diagnostics when the plugin itself is not the divergent layer.

## Evidence collection workflow

1. Record **Complaint**; **Vitals**; **Differential diagnosis**; **Confirmed diagnosis**; **Treatment**; **Post-treatment verification**; **Discharge summary or escalation packet** in that order.
2. Capture installed version, platform, active profile/home summary, plugin type, and surface. Redact private paths and identifiers.
3. For backend plugins, separate discovery/manifest, registration, enablement, import, requirement checks, and runtime execution.
4. For Desktop plugins, separate inventory, Desktop settings, hot reload, preload/IPC, renderer/UI reachability, and backend connection.
5. Use `hermes plugins list` and `hermes tools list --platform cli` only as bounded inventory evidence. Registration is not availability and availability is not successful runtime execution.
6. Inspect a named non-secret artifact only when identified by the operator. Do not upload plugin bundles, dump manifests containing secrets, or share raw logs.
7. Compare one controlled profile/surface at a time. A fresh session or reload may mutate caches or runtime state and requires approval.
8. Label every claim exactly as **Observed**, **Reproduced**, **Confirmed in installed source**, **Officially documented**, **Known upstream fix**, or **Hypothesis**.

## Decision tree

1. **Is the plugin on the intended plugin surface?**
   - No: classify inventory/profile/home or installation evidence; do not install it as a probe.
   - Yes: continue.
2. **Is the manifest valid and the plugin registered?**
   - No: classify source/discovery/registration; do not edit the manifest.
   - Yes: continue.
3. **Is enablement or a requirement gate suppressing the runtime surface?**
   - Yes: classify enablement/requirement; route tool exposure to `emh-tool-runtime-diagnostics`.
   - No: continue.
4. **Did import/backend runtime or Desktop preload/IPC reachability fail?**
   - Backend: separate import exception, handler, and backend dependency.
   - Desktop: separate main process, preload/IPC, renderer, and UI reachability.
5. **Would the next probe install, remove, enable, disable, reload, compile, or edit a plugin?**
   - Yes: stop for explicit approval, verified backup, rollback, and post-change verification.
   - No: collect the smallest remaining read-only evidence.

## Exact commands and tool calls

These commands were checked against current Hermes help/source. Run only the smallest relevant subset; plugin metadata and logs remain private until redacted.

### Read-only allowlist

- `hermes --version`
- `hermes status --all`
- `hermes plugins list`
- `hermes tools list --platform cli`
- `hermes logs list`
- `hermes logs --component tools -n 50 --level WARNING`
- `hermes logs desktop -n 50 --level WARNING`
- `read_file(path="<named-non-secret-plugin-artifact>")`

`hermes logs desktop -n 50 --level WARNING` is bounded Desktop runtime evidence for main, preload, renderer, and IPC failures. Keep it separate from backend plugin inventory (`hermes plugins list`) and tool inventory. The `read_file` path must be a named, non-secret artifact supplied by the operator. Bounded logs are evidence only after redaction; do not scan plugin directories or credential files.

### Approval-gated reproductions and mutations

- `hermes plugins install`, `update`, `remove`, `enable`, or `disable` changes plugin state.
- Plugin reload, Desktop launch/rebuild, toolset changes, registry overrides, dependency installation, and fresh-session launch can mutate runtime or cache state.
- Any tool invocation owned by a plugin inherits that tool’s approval, network, private-data, and backend boundaries.

Every proposed action requires explicit approval, a verified backup of the plugin/config state, a rollback procedure, an abort condition, and post-change verification. Never silently mutate plugin or runtime state or continue after an abort condition; no autonomous repair is permitted.

## Safety and approval boundaries

**Read-only first.** Never silently install, remove, enable, disable, reload, compile, edit, register, deregister, invoke, or replace a backend or Desktop plugin.

- Obtain explicit approval immediately before every lifecycle action or plugin-owned tool execution.
- Require a verified backup and credible rollback before changing plugin files, configuration, registry state, dependencies, or Desktop artifacts.
- Never treat backend registration as Desktop UI reachability, or a manifest as proof of import/runtime success.
- Redact credentials, private paths, endpoints, identifiers, plugin payloads, user content, screenshots, and raw logs. Keep evidence private until reviewed.
- A denial or failed requirement is evidence for that attempt; never silently retry through another surface.
- After an approved change, verify the same plugin surface, profile/home, session, and original symptom. Never silently broaden scope.

## Common pitfalls and recovery

- **Pitfall: backend registration produces no Desktop pane.** Recovery: classify backend and Desktop plugin surface separately.
- **Pitfall: a manifest entry proves runtime success.** Recovery: inspect registration, enablement, import, requirement, and runtime stages independently.
- **Pitfall: hot reload substitutes for fresh-session verification.** Recovery: record cache/session state and obtain approval before reload or fresh launch.
- **Pitfall: tool absence is automatically a plugin defect.** Recovery: preserve plugin inventory then trace toolset, schema, and dispatch separately.
- **Pitfall: changing enablement before classification.** Recovery: stop; collect read-only status and installed-source evidence first.
- **Pitfall: sharing an unredacted bundle or log.** Recovery: retain only a minimal redacted symbol, status, or bounded excerpt.

## Verification checklist

- [ ] Installed version, platform, profile/home summary, plugin type, and surface are recorded.
- [ ] Backend manifest/registration/enablement/import/runtime and Desktop inventory/settings/hot-reload/preload/UI stages are separate.
- [ ] Tool registration, interface reachability, and plugin runtime are not conflated.
- [ ] Every conclusion has one exact evidence label and adjacent bounded source.
- [ ] No plugin lifecycle, dependency, registry, reload, or tool execution mutation occurred without explicit approval.
- [ ] Any approved action has a verified backup, rollback, and same-surface post-change verification.
- [ ] Raw bundles, credentials, private paths, user content, identifiers, and raw logs are absent from shared evidence.
- [ ] Residual uncertainty is a falsifiable question.

## Escalation packet requirements

Provide a redacted, minimal packet containing:

- **Installed version:** exact Hermes version and install method if known.
- **Platform:** OS/version, active profile/home summary, surface, and Desktop/backend context.
- **Reproduction:** bounded inventory or read-only command sequence, plugin type/name class, profile, session, and surface.
- **Expected behavior:** expected plugin inventory, registration, enablement, import/runtime, or UI result.
- **Actual behavior:** first divergent plugin stage and structured status/error.
- **Minimal evidence:** plugin inventory, tool summary where relevant, named artifact excerpt, bounded log excerpt, and installed-source or official URL.
- **Plugin surface:** backend versus Desktop, manifest/inventory, registration, enablement, import/runtime, hot reload, preload/IPC, and UI reachability classification.
- **Residual question:** one concrete maintainer question that distinguishes the remaining Hypothesis.
- **Safety record:** read-only probes, explicit approvals, side effects, verified backup, rollback, and post-change verification.
- **Redaction boundary:** redact credentials, private paths, endpoints, plugin payloads, user content, IDs, screenshots, and raw logs; keep the packet private until reviewed.
