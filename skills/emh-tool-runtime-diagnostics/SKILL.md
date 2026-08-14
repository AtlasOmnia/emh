---
name: emh-tool-runtime-diagnostics
description: Use when a Hermes tool is absent, unavailable, denied, malformed, mis-dispatched, truncated, or dependent on a failing execution backend.
version: 0.2.0
author: Jonathan Rivera
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [diagnostics, tools, runtime, dispatch, approvals]
    related_skills: [emh-environment-diagnostics, emh-plugin-diagnostics]
---

# EMH tool runtime diagnostics

## Response presentation

Use the shared [EMH response reference](../emh-triage/references/response-templates.md) for normal answers: lead with **What I found**, **What it means**, **Safest next step**, **Permission needed: Yes/No**, then **Technical details**. Preserve this skill's domain workflow, evidence labels, and safety/approval rules; this presentation guidance does not replace them. Keep mutation, external-contact, sensitive-risk, safety, and data-loss warnings in the concise answer, and keep technical proof complete and redacted.

## Overview

Diagnose the complete tool path as separate gates:

1. module/plugin/MCP discovery and registration;
2. requirement or `check_fn` availability;
3. enabled/disabled toolset resolution for the active platform;
4. schema exposure to the model in the current session;
5. model-emitted name and arguments;
6. bridge, hooks, middleware, approval, and central dispatch;
7. handler and execution backend;
8. result contract, sanitization, and truncation;
9. fresh-session state after an approved configuration or registry change.

Installed source confirms that built-ins self-register into `tools/registry.py`, `model_tools.get_tool_definitions()` resolves/filter schemas, and `model_tools.handle_function_call()` dispatches through middleware to the registry. Catalog visibility, model schema exposure, authorization, execution, and result presentation are different facts.

Evidence priority is explicit: current runtime and installed source outrank generic guidance. The official docs are authoritative current documentation, but qualify current behavior against the installed version. Current entry points are https://hermes-agent.nousresearch.com/docs/user-guide/features/tools and https://hermes-agent.nousresearch.com/docs/developer-guide/tools-runtime.

## When to Use

Use when:

- A tool or toolset cannot be found, is registered unexpectedly, or appears on one platform/profile but not another.
- A requirement gate marks a tool unavailable even though its module is present.
- A tool is catalogued but its schema is absent from a model turn, stale in a session, or malformed.
- A call is denied, routed to the wrong handler, rejected for arguments, or fails inside a backend.
- Output is truncated, malformed, unsupported, or transformed after successful execution.

**Don't use for:** general profile/skill discovery without a concrete tool-runtime symptom; backend-vs-Desktop plugin lifecycle; interface rendering alone; provider inference failures before a tool call exists; host/sandbox mismatches without a tool-path symptom; or update recovery.

## Evidence collection workflow

1. Record **Complaint**; **Vitals**; **Differential diagnosis**; **Confirmed diagnosis**; **Treatment**; **Post-treatment verification**; **Discharge summary or escalation packet**.
2. Capture installed version, platform, active profile/home summary, surface, fresh-versus-resumed session, and enabled/disabled toolsets without printing private configuration.
3. **Discovery/registration:** confirm the exact tool name and owning toolset in the catalog or installed source. Registration is not availability.
4. **Requirement/check gate:** determine whether a `check_fn`, required executable, service, credential presence, or backend readiness suppresses schema exposure. Record only boolean/readiness summaries; never request a raw credential.
5. **Toolset resolution:** compare requested toolsets, platform preset, disabled subtraction, plugin/MCP ownership, and resolved tool names. A tool can be registered and intentionally out of scope.
6. **Schema exposure:** inspect the exact current-session schema with `tool_describe` when available. A catalog entry is not proof that the model received it in an older session.
7. **Call formation:** preserve only the tool name, argument keys/types, validation error, and call ID in redacted form. Separate malformed model arguments from a malformed registered schema.
8. **Approval/dispatch:** preserve the exact approval or denial result and identify whether the call reached bridge resolution, request middleware, approval, execution middleware, registry lookup, or the handler. Never route around a denial.
9. **Handler/backend:** separate handler exceptions from execution-backend unavailability, timeout, permissions, and process result.
10. **Result shaping:** identify the handler result type, structured error, sanitization, transformation hook, and explicit truncation marker. Truncation does not prove the handler failed.
11. If an approved enablement/registry change occurred, verify in a fresh session because tool schemas live in session context and caches can be version-specific.
12. Label every claim exactly as **Observed**, **Reproduced**, **Confirmed in installed source**, **Officially documented**, **Known upstream fix**, or **Hypothesis**.

## Decision tree

1. **Is the exact tool absent from `tool_search` and installed registration evidence?**
   - Yes: discovery/import/registration or plugin/MCP ownership differential.
   - No: continue.
2. **Is it registered but absent from `hermes tools list` or the resolved platform set?**
   - Yes: toolset enablement, platform preset, disabled subtraction, or stale configuration differential.
   - No: continue.
3. **Is the tool filtered by a failed requirement/check gate?**
   - Yes: classify missing requirement, unavailable service/binary, credential-presence gate, or backend readiness without exposing secrets.
   - No: continue.
4. **Is the catalog/schema visible but the model emits no call or a malformed call?**
   - No call: prompt/model/tool-choice or stale-session Hypothesis.
   - Malformed name/arguments: compare emitted keys/types with `tool_describe`; do not blame the handler before dispatch.
5. **Was the call denied or blocked?**
   - Yes: denial is the actual behavior and an authorization boundary. Stop; do not retry, rephrase, split, or substitute.
   - No: continue.
6. **Did central dispatch report unknown tool or unsupported result type?**
   - Unknown tool: stale schema, registration churn, or wrong profile/session.
   - Unsupported type: handler result-contract defect.
7. **Did the handler run?**
   - Handler exception: handler defect unless backend evidence identifies a lower layer.
   - Backend unavailable/timeout/permission: route to environment diagnostics with this call evidence.
8. **Is output explicitly truncated?**
   - Yes: result-budget/presentation classification; locate the bounded artifact or rerun only with approval if reproduction has side effects.
   - No: inspect result transformation and consumer rendering.

## Exact commands and tool calls

These were confirmed in installed help/source or current official documentation. Run only the smallest relevant subset.

### Read-only allowlist

- `hermes --version`
- `hermes status --all`
- `hermes tools --summary`
- `hermes tools list --platform cli`
- `hermes logs -n 50 --component tools --level WARNING`
- `tool_search(query="<capability>", limit=5)`
- `tool_describe(name="<exact-tool-name>")`

`tool_search` and `tool_describe` are pure catalog reads in the installed dispatcher. Bounded logs remain private until redacted. Do not run a target tool merely to prove it exists; execution safety depends on that tool and its backend.

### Approval-gated reproductions and mutations

- `hermes tools enable --platform cli <toolset>` changes persistent per-platform enablement.
- `hermes tools disable --platform cli <toolset>` changes persistent per-platform enablement.
- Starting a fresh interactive session to refresh schemas can create session/log/cache state.
- `tool_call(name="<exact-tool-name>", arguments={})` executes the underlying tool and inherits every approval, side effect, network, backend, and data boundary of that tool.
- Plugin/MCP reload, post-setup installation, registry override, requirement installation, provider/credential changes, and backend changes require explicit approval.

Before mutation, record exact scope, verified backup, rollback, expected schema/result change, and the fresh-session verification. Never use YOLO/approval-off as a diagnostic shortcut.

## Safety and approval boundaries

**Read-only first.** Never silently enable, disable, install, reload, register, deregister, override, invoke, retry, reconfigure, or change a backend.

- Obtain explicit approval for every tool execution that can write, send, upload, spend, start/stop processes, contact a network, or expose private data.
- A structured denial, hard block, or user refusal is authoritative. Preserve it as evidence and stop without alternate dispatch.
- Require a verified backup and credible rollback before persistent toolset, plugin, MCP, config, or backend changes.
- Never request raw keys, tokens, environment dumps, schemas containing private defaults, complete arguments, raw logs, or unredacted results.
- Treat tools shown by an old session as stale until a fresh session proves current exposure; do not delete a session to test this.
- Do not mistake registration for availability, schema visibility for authorization, authorization for execution, or execution for untruncated delivery.

## Common pitfalls and recovery

- **Pitfall: “tool not found” means not installed.** Recovery: check discovery/registration, toolset resolution, requirement gate, schema exposure, and current-session age in order.
- **Pitfall: catalog visibility proves model visibility.** Recovery: compare `tool_search`/`tool_describe` with the exact session's exposed schemas or reproduce in an approved fresh session.
- **Pitfall: requirement failure is treated as registration failure.** Recovery: preserve the `check_fn`/readiness result separately and test only the missing requirement with a bounded read-only probe.
- **Pitfall: malformed call blamed on handler.** Recovery: compare emitted name and argument keys/types with the schema before checking dispatch logs.
- **Pitfall: retrying a denial through `execute_code`, shell, or another surface.** Recovery: stop, record denial verbatim after redaction, and request a new explicit approval only if the operator changes scope.
- **Pitfall: truncation treated as failed execution.** Recovery: record return status and truncation marker separately; use an existing bounded spill/artifact if the tool provides one.
- **Pitfall: enabling a tool and checking the same stale session.** Recovery: preserve the session, start an approved fresh one, and verify exposure without invoking the tool.
- **Pitfall: handler and backend errors conflated.** Recovery: identify whether dispatch reached the handler and whether the backend created a process/request before assigning root cause.

## Verification checklist

- [ ] Exact tool name, owning toolset, installed version, platform, profile/home summary, and session age are recorded.
- [ ] Discovery, requirement/check gate, toolset resolution, schema exposure, call formation, approval, dispatch, handler/backend, and result shaping are reported separately.
- [ ] Registration, denial, malformed schema/call, truncation, and handler/backend failure classifications are explicit.
- [ ] Every conclusion has one exact evidence label and adjacent bounded source.
- [ ] No denied call was retried or routed around.
- [ ] No credential, private argument, raw log, or unredacted tool result is present.
- [ ] Any approved persistent change has a verified backup, rollback, and fresh-session verification.
- [ ] The original symptom, not merely catalog presence, was rechecked.

## Escalation packet requirements

Provide a redacted, minimal packet containing:

- **Installed version:** exact Hermes version and install method if known.
- **Platform:** OS, interface/platform preset, execution backend, active profile/home summary, and fresh/resumed session state.
- **Reproduction:** exact bounded prompt or call sequence, tool name, argument keys/types, and approval result.
- **Expected behavior:** expected discovery, schema, dispatch, execution, or result state.
- **Actual behavior:** first divergent gate and structured status/error.
- **Minimal evidence:** catalog result, toolset/check summary, schema excerpt limited to relevant keys, redacted call/result, truncation marker, and installed-source symbol/official URL.
- **Pipeline classification:** registration, requirement gate, toolset, schema, malformed call, denial, dispatch, handler/backend, result shaping, and fresh-session findings.
- **Residual question:** one concrete question that distinguishes the remaining Hypotheses.
- **Safety record:** read-only probes, approvals, side effects, backup/rollback, and fresh-session verification.
- **Redaction boundary:** redact credentials, arguments containing user data, local paths, endpoints, IDs, and results. Keep the packet private until reviewed; never attach raw logs, full schemas with private defaults, or complete tool payloads.
