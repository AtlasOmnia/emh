# EMH v0.2 Skill Expansion Plan and Coverage Matrix

> **For Hermes:** Execute with one repository writer at a time, strict vertical RED → GREEN evidence, controller-owned gates, and no live Hermes mutation.

**Goal:** Expand EMH from domain triage into complete class-level diagnostics for interfaces, tool runtime, execution environments, and update recovery without duplicating the eight v0.1 domain owners.

**Frozen baseline:** commit `8fa0c3e3d8d34ff2a593c38bd150f978268ad69f`, tree `114aa648b7a5042f56f1f3fc87307a44aff3ba15`, `127 passed`. The controller re-ran the baseline suite before this plan was written and observed `127 passed`.

**Authority order:** current runtime evidence; installed source and tests; version-matched official release evidence; current official documentation; then explicitly labeled hypotheses. Current documentation is authoritative documentation, but it does not override behavior confirmed in the installed runtime.

## Discovery basis

The audit read every existing product skill, support file, script, and test; checked the installed CLI help and relevant installed source; and compared current official documentation for CLI, TUI, Desktop, tools runtime, terminal backends, security approvals, and updating.

Primary current sources:

- https://hermes-agent.nousresearch.com/docs/user-guide/cli
- https://hermes-agent.nousresearch.com/docs/user-guide/tui
- https://hermes-agent.nousresearch.com/docs/user-guide/desktop
- https://hermes-agent.nousresearch.com/docs/user-guide/features/tools
- https://hermes-agent.nousresearch.com/docs/developer-guide/tools-runtime
- https://hermes-agent.nousresearch.com/docs/user-guide/configuration
- https://hermes-agent.nousresearch.com/docs/user-guide/security
- https://hermes-agent.nousresearch.com/docs/getting-started/updating
- https://hermes-agent.nousresearch.com/docs/user-guide/windows-native

## Coverage matrix

| Declared responsibility | Existing owner | Observed v0.1 coverage | Gap or overlap | v0.2 disposition |
| --- | --- | --- | --- | --- |
| Profiles | `emh-profile-session-skill-diagnostics` | Active profile, effective Hermes home, isolation, and cross-invocation comparison | No material gap | Keep existing owner unchanged |
| Memory | `emh-memory-diagnostics` | Built-in facts versus session snapshot and optional provider state | No material gap | Keep existing owner unchanged |
| Kanban | `emh-kanban-diagnostics` | Queue, dispatcher, gateway, worker lifecycle, workspace, and profile boundaries | No material gap | Keep existing owner unchanged |
| Plugins | `emh-plugin-diagnostics` | Backend and Desktop plugin systems; inventory, enablement, import, runtime, and UI separation | Interface symptoms can originate in a plugin, but plugin lifecycle remains here | Keep existing owner; interface skill hands plugin evidence to it |
| Gateways | `emh-gateway-diagnostics` | Service, adapter auth, provider inference, session route, and outbound delivery layers | Desktop's `hermes serve` backend is not a messaging gateway; shallow naming overlap only | Keep gateway owner; interface skill classifies the process before handoff |
| Providers and models | `emh-provider-diagnostics` | Configuration, reachability, authentication, model capability, fallback, limits, and privacy | Interface and tool failures can expose provider errors but do not own provider diagnosis | Keep existing owner; new skills hand off confirmed provider-layer failures |
| Skills and sessions | `emh-profile-session-skill-diagnostics` | Session storage versus active context; skill discovery, frontmatter, enablement, and fresh-session effects | Tool registration is mentioned only to preserve the discovery boundary | Keep existing owner; tool runtime starts after discovery/registration evidence |
| Tools | `emh-profile-session-skill-diagnostics` has a narrow boundary mention | Skill discovery versus tool registration and per-platform enablement | Material gap: requirements gates, toolset resolution, schema exposure, dispatch, approvals, backend routing, truncation, malformed calls, and stale-session state | Add `emh-tool-runtime-diagnostics` |
| CLI, TUI, and Desktop | `emh-profile-session-skill-diagnostics` performs only a constant-profile comparison | Cross-surface comparison with profile and home held constant | Material gap: CLI routing and prompt-toolkit, TUI Node/TTY/render/input transport, Desktop renderer/main/backend/bridge separation, CDP evidence, and startup logs | Add `emh-interface-diagnostics` |
| Updates and recovery | `emh-release-intelligence` | Installed version, install method, source state, official release comparison | Material gap: readiness, backups, interrupted updates, lock/process evidence, rollback planning, post-update verification, and approval gates | Add `emh-update-recovery`; keep release intelligence read-only and reusable |
| Supported operating systems and execution environments | `emh-triage` has only a routing row | Platform is captured as a vital | Material gap: macOS/Linux/Windows/WSL and local/Docker/SSH/Modal/Daytona/Vercel Sandbox/Singularity boundaries; host versus backend evidence | Add `emh-environment-diagnostics` |

## Umbrella decisions

All four candidates are distinct class-level workflows. None is a narrow symptom skill, and no existing umbrella owns most of any candidate.

| Umbrella | Distinct trigger | Distinct workflow | Evidence model | Characteristic pitfalls | Verification boundary |
| --- | --- | --- | --- | --- | --- |
| `emh-interface-diagnostics` | One or more interactive surfaces fail to start, route, render, accept input, or agree | Hold profile/home/session constant; identify classic CLI, TUI, or Desktop; split frontend, transport, backend, provider, and gateway layers; use read-only renderer inspection when available | Terminal capability and key sequence evidence; frontend status; backend process/transport evidence; bounded redacted Desktop logs; optional read-only CDP state | Treating a blank renderer as a dead backend; calling terminal key interception a Hermes keybinding bug; confusing `hermes serve` with messaging gateway; changing profiles during comparison | Original surface works with the same profile/home/session, or the fault is handed to its owning domain with layer evidence |
| `emh-tool-runtime-diagnostics` | A tool is absent, unavailable, denied, malformed, dispatched incorrectly, truncated, or behaves differently by platform/backend | Walk discovery → requirements → toolset resolution → schema exposure → dispatch → approval → backend execution → result shaping → fresh-session check | Registry/toolset inventory, `check_fn` state, exposed schema, dispatch/error class, approval result, backend identity, bounded result metadata | Treating registration as availability; retrying execution-layer denial; blaming a handler for backend isolation; treating truncated output as successful completion; using a stale session after toolset changes | Same call reaches the intended handler/backend with a valid bounded result, or a precise owning-layer escalation is produced |
| `emh-environment-diagnostics` | Behavior differs by OS, WSL boundary, host, container, remote host, or cloud execution backend | Record host and execution backend separately; compare paths, permissions, environment, network, process, persistence, and artifact location; reproduce with a minimal cross-platform packet | Two-column host/backend observations plus platform/runtime/backend versions and boundary-specific probes | Reporting host facts as container facts; assuming filesystem persistence preserves processes; confusing Windows and WSL homes; forwarding private environment data; testing the wrong filesystem | Reproduction identifies both host and execution location and either converges across environments or isolates one boundary |
| `emh-update-recovery` | An update is being considered, is interrupted/failed, or requires rollback/recovery and post-update validation | Reuse offline release intelligence; identify install method and source state; assess readiness and verified backup/rollback; inspect bounded update evidence; classify stage; propose only approval-gated update/restart/restore actions; repeat post-update checks | Before/after version, Git/source state, process/lock stage, backup identity and verification, bounded update-log summary, service status | Treating `hermes update --check` as an install; updating a dirty tree blindly; forcing Windows venv mutation; restoring an unverified backup; checking out a commit without config compatibility review | Version/source/config/service checks match the approved target, original symptom is repeated, and rollback remains available until acceptance |

### Why these are additions rather than extensions

- `emh-profile-session-skill-diagnostics` owns identity, storage/context, discovery, and enablement. It does not own terminal rendering, Electron process architecture, registry dispatch, approvals, or execution backends.
- `emh-release-intelligence` explicitly stops at read-only assessment. Adding update execution and recovery would erase its safe trigger and evidence boundary.
- `emh-triage` is the master case router. Turning it into a platform/backend manual would make every complaint load unrelated operating-system detail.
- `emh-plugin-diagnostics`, `emh-gateway-diagnostics`, and `emh-provider-diagnostics` remain downstream domain owners after an interface or tool-runtime workflow proves the fault is in those layers.

## Ownership and handoff rules

1. Profile, Hermes home, session selection, and skill discovery remain with `emh-profile-session-skill-diagnostics`.
2. Tool runtime begins at requirements gating and schema exposure; it hands environment failures to `emh-environment-diagnostics`, provider failures to `emh-provider-diagnostics`, and plugin registration/import failures to `emh-plugin-diagnostics`.
3. Interface diagnostics owns frontend startup/render/input and Desktop frontend-to-backend transport. It hands confirmed provider, gateway, profile, plugin, or tool failures to those owners.
4. Environment diagnostics owns the host/backend boundary, not tool schema or handler correctness.
5. Update recovery consumes release-intelligence evidence but never changes the read-only contract of `emh-release-intelligence`.

## Version policy

- Distribution version: `0.2.0`.
- New capability umbrellas: `0.2.0`.
- Existing v0.1 skills remain `0.1.0` when their files are untouched; this records the version in which that stable contract last changed.
- Any existing skill changed during this campaign must be upgraded to `0.2.0` and satisfy the complete v0.2 quality contract.
- Tests must assert the exact name-to-version inventory so mixed versions are deliberate, not accidental.
- No tag or release is created by this campaign.

## Vertical TDD slices

### Slice 1 — exact inventory and frontmatter

1. Add focused tests for the exact twelve-skill inventory and explicit version map.
2. Require byte-zero YAML, lowercase hyphenated names, trigger-first descriptions, author, license, platforms, tags, and related skills for every new skill.
3. Run the focused test RED because the four new skills do not exist.
4. Add only the minimum frontmatter and section skeleton needed for the same focused test to pass.

### Slice 2 — trigger, counter-trigger, workflow, and safety contracts

1. Add focused parsed-Markdown tests for each new umbrella's required sections, precise trigger and `Don't use for` counter-triggers, exact claim labels, read-only-first rule, explicit approval, verified backup/rollback, and escalation packet.
2. Run RED against the skeleton.
3. Implement the four complete diagnostic workflows and run the identical focused test GREEN.

### Slice 3 — executable evidence and command boundaries

1. Add semantic tests that extract fenced command blocks and compare them with the documented read-only allowlist and approval-gated action set.
2. Prove interface diagnostics separates CLI/TUI/Desktop layers; tool runtime separates registration/dispatch/approval/backend/result; environment diagnostics separates host/backend and every supported backend; update recovery separates assessment/readiness/interruption/rollback/post-update stages.
3. Run RED, implement the missing evidence tables/decision trees/commands, then run identical GREEN.

### Slice 4 — repository safety and regression gates

1. Extend public-safety coverage without weakening any existing rule. Keep strict UTF-8 and binary failure; scan tracked and untracked files; allow only exact redaction tokens.
2. Add a test-time network guard so ordinary tests fail on unexpected socket connection attempts; explicitly opt in only a bounded local fixture if one is ever required.
3. Snapshot protected live-state paths and environment metadata before and after the suite without reading secret content; assert tests do not create or modify them.
4. Re-run all existing `collect_vitals` and `source_status` behavior tests unchanged.

## Gate taxonomy

- **Pre-flight gate:** correct branch/baseline, clean index/tree, no competing writer, one worktree, no remotes/tags/locks. Failure action: HOLD. Resume only when the frozen baseline is restored or the operator authorizes a new baseline.
- **Revision gate:** each focused RED must fail for the intended missing contract; each matching GREEN uses the same command. A writer gets at most three materially different correction attempts before escalation.
- **Escalation gate:** ambiguous installed-versus-current behavior, missing official evidence, or a destructive recovery decision. Preserve evidence and ask the operator; never guess.
- **Abort gate:** live Hermes mutation, secret/private material, remote/tag/publish activity, competing writer, or unresolvable verification failure. Stop and preserve the repository state.

## Required closeout gates

Run with the controller-provided Hermes Python and external pytest path without installing dependencies:

```bash
python -m pytest -q
python -m py_compile path/to/each/repository-script.py
git diff --check
git status --short --untracked-files=all
git remote -v
git tag --list
git worktree list --porcelain
```

Also verify every repository script is mode `755`, run the public-safety scanner directly, confirm strict invalid UTF-8/binary fixtures fail closed, and compare protected live-state snapshots. Verification must not invoke an update, restart, install, reset, restore, delete, provider/model switch, upload, publish, or live profile installation.

## Initial resume state

Coverage audit complete. Baseline gate and baseline suite pass. No product skill or test for v0.2 has been written. Next action: commit this matrix and the initial changelog, then delegate one sole writer to execute Slice 1 with an append-only RED/GREEN evidence ledger outside the repository.
