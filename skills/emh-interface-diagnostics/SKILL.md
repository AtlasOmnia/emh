---
name: emh-interface-diagnostics
description: Use when Hermes CLI, TUI, or Desktop surfaces fail to start, route, render, accept input, stream, or agree across the same session.
version: 0.2.0
author: Jonathan Rivera
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [diagnostics, interface, cli, tui, desktop]
    related_skills: [emh-profile-session-skill-diagnostics, emh-gateway-diagnostics]
---

# EMH interface diagnostics

## Response presentation

Use the shared [EMH response reference](../emh-triage/references/response-templates.md) for normal answers: lead with **What I found**, **What it means**, **Safest next step**, **Permission needed: Yes/No**, then **Technical details**. Preserve this skill's domain workflow, evidence labels, and safety/approval rules; this presentation guidance does not replace them. Keep mutation, external-contact, sensitive-risk, safety, and data-loss warnings in the concise answer, and keep technical proof complete and redacted.

## Overview

Use this class-level workflow to locate a failure in one of three front ends without blaming the shared agent prematurely:

- **Classic CLI:** Python argument routing, the `prompt_toolkit` REPL, terminal input/keybindings, and the shared agent runtime.
- **TUI:** Python launch routing, Node.js and TTY readiness, the built bundle, TypeScript rendering/input/keybindings, JSON-RPC transport, and the shared Python runtime.
- **Desktop:** Electron main process, preload/IPC bridge, React renderer, local or remote `hermes serve` backend, and the shared agent runtime.

Hold runtime version, effective profile/home, working directory, model/provider, toolsets, and session identity constant before comparing surfaces. A provider, gateway, profile, plugin, tool, or backend defect can appear through an interface without being an interface defect.

Evidence priority is explicit: current runtime and installed source outrank generic guidance. The official docs are authoritative current documentation, but qualify every documented claim when the installed version differs. Current entry points are https://hermes-agent.nousresearch.com/docs/user-guide/cli, https://hermes-agent.nousresearch.com/docs/user-guide/tui, and https://hermes-agent.nousresearch.com/docs/user-guide/desktop.

## When to Use

Use when:

- CLI routing selects the wrong mode, the classic prompt fails, or terminal keybindings/input differ from documented behavior.
- TUI startup fails before first frame, rendering corrupts, input is ignored, a keybinding diverges, or its transport stops carrying events.
- Desktop boot, renderer, preload bridge, backend connection, streaming, or native input differs from CLI/TUI under the same identity.
- One surface works and another fails, and the failing layer has not been classified.

**Don't use for:** provider-only inference failures reproduced identically on every surface; gateway adapter or outbound-delivery incidents; backend-vs-Desktop plugin lifecycle questions; missing or denied tools; host/execution-backend mismatches; or update recovery. Route those to the related domain skill after collecting only the interface boundary evidence.

## Evidence collection workflow

1. Record the case labels in order: **Complaint**; **Vitals**; **Differential diagnosis**; **Confirmed diagnosis**; **Treatment**; **Post-treatment verification**; **Discharge summary or escalation packet**.
2. Capture the installed version, platform, launch command, effective profile/home summary, terminal application, TTY state, and whether the same session is being resumed. Redact local paths and identifiers.
3. Reproduce one surface at a time with the same provider, model, profile, home, working directory, toolsets, and session. A new launch or session can write state, so obtain approval before that reproduction.
4. For CLI, split parser/routing from `prompt_toolkit`, input/keybindings, rendering, and shared-runtime output.
5. For TUI, split Python routing from Node/TTY/bundle readiness, rendering, input/keybindings, transport, and Python runtime. Installed source confirms the TUI is a Node front end over the shared runtime; do not treat a TUI rendering symptom as proof of an agent failure.
6. For Desktop, split Electron main-process boot and backend ownership from preload/IPC bridge, React renderer, backend WebSocket/JSON-RPC, and agent behavior. Installed source places install/backend/self-update logic in the main process and exposes a bounded preload bridge to the renderer.
7. Use read-only CDP only when a development renderer already exposes it. Project to a small value such as title, element count, or computed style; do not dump the DOM. Use a background capture for visual evidence without clicking or typing.
8. Compare the same request on one known-good surface only after controlling identity. If both surfaces fail identically, move the differential below the interface.
9. Label each claim exactly:
   - **Observed** — directly present in bounded runtime or capture evidence.
   - **Reproduced** — repeated with controlled, approved steps.
   - **Confirmed in installed source** — tied to a file, symbol, or installed test.
   - **Officially documented** — tied to an adjacent current official URL and version caveat.
   - **Known upstream fix** — tied to an official, version-matched release or commit.
   - **Hypothesis** — plausible and paired with a falsification step.

## Decision tree

1. **Does the symptom reproduce in CLI, TUI, and Desktop with identity held constant?**
   - Yes: classify provider, gateway, profile/session, plugin, tool, or backend before touching interface code.
   - No: continue at the first surface-specific boundary.
2. **Classic CLI only?**
   - Wrong mode before prompt: parser/routing or config-precedence differential.
   - Prompt starts but input/keybinding fails: TTY, terminal emulator, `prompt_toolkit`, or keybinding differential.
   - Input submits but response/tool display fails: shared runtime, event shaping, or renderer differential.
3. **TUI only?**
   - No first frame: Node version, TTY, bundle/dependency, or Python launcher differential.
   - Frame appears but text/input is wrong: TypeScript render/composer/keybinding differential.
   - Local input works but events stop: stdio or loopback WebSocket JSON-RPC transport differential; do not confuse it with the OpenAI-compatible gateway API.
   - Agent reports the same error in CLI: leave the TUI branch and classify the shared layer.
4. **Desktop only?**
   - App does not boot or backend never becomes ready: Electron main process, install resolution, backend spawn, or backend health.
   - Window renders but native actions fail: preload/IPC bridge or main-process handler.
   - Backend is healthy but components are wrong: React renderer/state.
   - Local backend works but remote mode fails: authentication/network/remote `hermes serve`, not renderer by default.
5. **Only a plugin pane or tool row fails?** Route to plugin or tool-runtime diagnostics after preserving the interface evidence.

## Exact commands and tool calls

These were confirmed in installed help/source or current official documentation. Run only the smallest relevant subset.

### Read-only allowlist

- `hermes --help`
- `hermes --version`
- `hermes status --all`
- `node --version`
- `hermes logs -n 50 --component cli --level WARNING`
- `hermes logs desktop -n 50 --level WARNING`
- `browser_cdp(method="Target.getTargets", params={})`
- `browser_cdp(method="Runtime.evaluate", params={"expression":"document.title","returnByValue":true}, target_id="<renderer-target-id>")`
- `computer_use(action="capture", mode="som", app="Hermes")`

Treat bounded log output as private until redacted. `browser_cdp` requires an already reachable development CDP endpoint; packaged Desktop builds deliberately keep it closed. `Runtime.evaluate` is read-only only for the literal expression above or an equally reviewed projection with no assignment, event dispatch, setter, or function that mutates state. A capture is observation; any click, key, drag, scroll, or text input is not on this allowlist.

### Approval-gated reproductions and mutations

- `hermes --cli` and `hermes --tui` start interactive runtime state; first TUI launch may install Node dependencies or rebuild its bundle.
- `hermes desktop --skip-build` launches the existing Desktop artifact and its backend; plain `hermes desktop` may install dependencies and build.
- `hermes config set display.interface tui` changes persistent configuration.
- Any CDP expression beyond a reviewed read-only projection, any `computer_use` input action, any app/backend restart, and any session/profile/plugin/tool change requires explicit approval.

Record the exact approved scope, expected effect, verified backup when state could change, rollback procedure, and post-change reproduction before acting.

## Safety and approval boundaries

**Read-only first.** Never silently launch, rebuild, install, configure, restart, reconnect, reload, click, type, switch profile/model/provider, change a session, or edit interface state.

- Obtain explicit approval before any runtime launch that can create session/log/cache state and before every mutation.
- Require a verified backup and tested or mechanically credible rollback before destructive or difficult-to-reverse configuration, profile, session, plugin, or application changes.
- Do not relaunch or kill the user's Desktop app to obtain CDP. If no approved read-only endpoint exists, collect capture and installed-source evidence or use an explicitly approved isolated instance.
- Do not use CDP to dump messages, tokens, the full DOM, storage, cookies, or private renderer state. Do not share raw logs or unredacted screenshots.
- A provider/gateway/profile/plugin/tool/backend error shown by a surface is not permission to mutate that other subsystem.
- A denial or execution-layer refusal is final evidence for that attempt; do not retry through another interface.

## Common pitfalls and recovery

- **Pitfall: comparing different profiles or homes.** Recovery: record redacted identity on both surfaces, align only with approval, then repeat the smallest reproduction.
- **Pitfall: calling every TUI failure “Node.”** Recovery: classify first-frame, render, input, keybinding, transport, and runtime stages separately; verify `node --version` without launching TUI.
- **Pitfall: treating a TUI `/api/ws` failure as a messaging gateway failure.** Recovery: identify the owning process and transport; current docs distinguish the dashboard/TUI JSON-RPC channel from the OpenAI-compatible gateway API.
- **Pitfall: treating a Desktop renderer error as a backend crash.** Recovery: gather main-process/backend readiness, preload bridge result, renderer error, and backend event separately.
- **Pitfall: launching plain `hermes desktop` as a probe.** Recovery: stop before build/install; use status, bounded logs, capture, installed source, or an approved existing artifact.
- **Pitfall: stale CDP target or broad DOM dump.** Recovery: refresh the target list, select the main renderer by URL/title, and project one bounded fact.
- **Pitfall: changing keybindings to test keybindings.** Recovery: record terminal, TTY, key sequence, expected action, actual action, and compare a documented alternate key without persistent edits.
- **Pitfall: sharing a screenshot or log containing prompts, paths, IDs, or credentials.** Recovery: discard the shareable copy, redact locally, and retain only the minimal structural excerpt.

## Verification checklist

- [ ] Installed version, platform, interface, launch mode, profile/home summary, working directory, and session identity are recorded.
- [ ] Provider, gateway, profile, plugin, tool, backend, and interface defects are not conflated.
- [ ] CLI parser/`prompt_toolkit`; TUI Node/TTY/bundle/render/input/keybindings/transport; or Desktop main/preload/renderer/backend layers are separated as applicable.
- [ ] Every conclusion uses one exact evidence label with adjacent command, source symbol, capture, or official URL.
- [ ] The known-good comparison held identity constant and did not silently create or alter live state.
- [ ] CDP/capture evidence is bounded, read-only, and redacted; raw logs and full DOM content are absent.
- [ ] Any approved change has a verified backup, rollback, and repeat of the original reproduction.
- [ ] Residual uncertainty is stated as a falsifiable question.

## Escalation packet requirements

Provide a redacted, minimal packet containing:

- **Installed version:** exact Hermes version and install method if known.
- **Platform:** OS family/version, native/WSL status, terminal/Desktop build, Node version for TUI, and interface.
- **Reproduction:** bounded steps, launch mode, controlled profile/home/session summary, and whether a fresh session was used.
- **Expected behavior:** one surface-specific result.
- **Actual behavior:** one surface-specific result and failure stage.
- **Minimal evidence:** exit status, bounded warning/error excerpt, small capture or CDP projection, and installed-source symbol/official URL where relevant.
- **Layer comparison:** CLI, TUI, Desktop, provider, gateway, profile, plugin, tool, and backend results kept distinct.
- **Residual question:** one concrete maintainer question that would resolve the remaining Hypothesis.
- **Safety record:** read-only probes performed, approved actions performed, backup/rollback status, and post-change verification.
- **Redaction boundary:** redact credentials, prompts, local paths, account/session/profile IDs, private endpoints, and personal content. Mark the packet private until reviewed; never attach raw logs, full screenshots, DOM dumps, or credential-bearing state.
