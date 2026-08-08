---
name: emh-kanban-diagnostics
description: Use when Hermes Kanban queue, dispatcher, gateway, worker, task run, or worker log state appears stuck or inconsistent.
version: 0.2.0
author: Jonathan Rivera
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [diagnostics, kanban, queue, workers, runs]
    related_skills: [emh-gateway-diagnostics, emh-profile-session-skill-diagnostics]
---

# EMH Kanban diagnostics

## Overview

Separate queue and board state from dispatcher/gateway state and from worker spawn, run, heartbeat, and log state. A task can be queued while the dispatcher is healthy, claimed while no worker is running, or completed while a stale log remains. Keep board, assignee, workspace, profile, task, and run identifiers scoped and redacted.

Evidence priority is explicit: current runtime and installed source outrank generic guidance. The official docs are authoritative current documentation, but current Kanban behavior must be checked against the installed Hermes version and board schema.

## When to Use

Use when:

- A Kanban task is stuck in queue, claimed, dispatched, spawned, running, failed, or completed state.
- Queue counts disagree with dispatcher or gateway status, worker liveness, task runs, or worker logs collected through bounded `hermes kanban log --tail 200 <task-id>` evidence.
- Board, assignee, workspace, profile, task, or run scope appears mixed.
- A read-only classification is needed before considering reclaim, reassign, unblock, complete, dispatch, restart, or repair.

**Don't use for:** generic gateway delivery failures without a Kanban task; provider inference failures; plugin lifecycle; profile/session isolation; memory; interface rendering; tool registration; environment/backend mismatch; or update recovery. Preserve only the smallest queue/worker evidence and route the incident to the owning domain when no task/run boundary is involved.

## Evidence collection workflow

1. Record **Complaint**; **Vitals**; **Differential diagnosis**; **Confirmed diagnosis**; **Treatment**; **Post-treatment verification**; **Discharge summary or escalation packet** in that order.
2. Capture installed version, platform, active profile/home summary, board slug, task identifier, assignee, workspace class, and session scope. Redact private paths and identifiers.
3. Run queue and board reads first. Distinguish board inventory, status counts, task state, assignee, and workspace from dispatcher behavior.
4. Inspect `hermes gateway status` separately. The Kanban dispatcher runs through the gateway in current Hermes; gateway health does not prove a worker spawned.
5. Classify the task lifecycle: queued, claimed, dispatched, spawned, running, failed, or completed. Use only the named task's bounded `hermes kanban log --tail 200 <task-id>` worker-log evidence, retaining the smallest necessary output after redaction.
6. Compare worker process/liveness, run outcome, heartbeat, and bounded `--tail 200` log timestamps, retaining only the smallest necessary redacted output. A stale log is not a current run result.
7. Reproduce only with a read-only command. Any dispatch, claim, reclaim, reassign, unblock, complete, repair, or worker launch is approval-gated.
8. Label every claim exactly as **Observed**, **Reproduced**, **Confirmed in installed source**, **Officially documented**, **Known upstream fix**, or **Hypothesis**.

## Decision tree

1. **Is the task visible on the intended board?**
   - No: classify board/profile/session scope or archival state; do not create a replacement task.
   - Yes: continue.
2. **Is queue state inconsistent with dispatcher/gateway state?**
   - Yes: classify queue versus dispatcher/worker boundary; do not reclaim or dispatch automatically.
   - No: continue.
3. **Was the task claimed or dispatched?**
   - No: classify queue/eligibility/assignee state.
   - Yes: continue.
4. **Did a worker spawn and produce a run?**
   - No: classify spawn/process/backend evidence and route environment/tool evidence as needed.
   - Yes: continue.
5. **Is the run running, failed, or completed while the task state disagrees?**
   - Yes: compare run outcome, heartbeat, event ordering, and bounded `hermes kanban log --tail 200 <task-id>` log timestamps, retaining only the smallest necessary redacted output.
   - No: preserve the remaining Hypothesis without changing task state.
6. **Would the proposed treatment mutate a task, board, worker, gateway, or workspace?**
   - Yes: stop for explicit approval, verified backup, rollback, and post-change verification.

## Exact commands and tool calls

These commands were checked against current Hermes help/source. Run only the smallest relevant subset; Kanban output and logs remain private until redacted.

### Read-only allowlist

- `hermes --version`
- `hermes status --all`
- `hermes kanban stats`
- `hermes kanban list`
- `hermes kanban runs <task-id>`
- `hermes kanban log --tail 200 <task-id>`
- `hermes gateway status`
- `hermes logs gateway -n 50 --level WARNING`

The `runs` and bounded `--tail 200` `log` commands require a named task ID. Use a task identifier supplied by the operator, never a broad scan. Preserve only the smallest necessary output and redact it before sharing. Do not use `kanban tail`, live follow, `watch`, or `dispatch` as a diagnostic shortcut.

### Approval-gated reproductions and mutations

- `hermes kanban claim`, `dispatch`, `reclaim`, `reassign`, `unblock`, `complete`, `repair`, or workspace changes mutate task or worker state.
- `hermes gateway start`, `restart`, or `stop` changes service state.
- Any worker launch, live watch, task creation/edit, comment, attachment, or log export requires explicit approval.

Every proposed action must name scope, expected effect, a verified backup where state exists, rollback, abort condition, and post-change verification. Never silently mutate task, worker, gateway, or workspace state or continue after an abort condition. No autonomous repair is permitted.

## Safety and approval boundaries

**Read-only first.** Never silently claim, dispatch, reclaim, reassign, unblock, complete, edit, repair, archive, delete, restart, stop, or start a task, board, worker, gateway, or workspace.

- Obtain explicit approval immediately before each mutation; read-only investigation approval does not authorize treatment.
- Require a verified backup or export appropriate to the board state and a credible rollback before difficult-to-reverse changes.
- Never bypass a live claim, worker, dispatcher lock, or gateway process. Preserve the first failure and do not run a second dispatcher to “test” it.
- Redact task titles, prompts, workspace paths, profile/session IDs, message IDs, credentials, private endpoints, and raw logs. Keep raw logs private.
- After an approved change, verify task state, run state, worker/gateway state, and the original symptom. Never silently widen to another board or profile.

## Common pitfalls and recovery

- **Pitfall: queue count proves dispatcher health.** Recovery: compare queue, gateway, dispatcher, worker spawn, run, heartbeat, and log stages.
- **Pitfall: a claimed task proves a worker is running.** Recovery: inspect the named run, worker liveness, and event timestamps.
- **Pitfall: a stale worker log is current evidence.** Recovery: use only `hermes kanban log --tail 200 <task-id>`, match log timestamps and task/run identity, and retain the smallest necessary redacted excerpt; never use `kanban tail` or live follow.
- **Pitfall: mixing boards or profiles.** Recovery: record board slug, assignee, workspace class, profile, and task scope before comparison.
- **Pitfall: reclaiming before classifying spawn.** Recovery: stop; determine whether the worker spawned, failed, or is still live.
- **Pitfall: retrying dispatch after denial or failure.** Recovery: preserve the denial/first error and request new explicit approval for a changed scope.

## Verification checklist

- [ ] Installed version, platform, board, profile/home, task, assignee, workspace, and session scope are recorded.
- [ ] Queue/board, dispatcher/gateway, worker spawn, run, heartbeat, and bounded `hermes kanban log --tail 200 <task-id>` worker-log evidence are separate; only the smallest necessary redacted output is retained.
- [ ] Queued, claimed, dispatched, spawned, running, failed, and completed state transitions are explicit.
- [ ] Every conclusion has one exact evidence label and adjacent bounded source.
- [ ] No task, board, worker, gateway, or workspace mutation occurred without explicit approval.
- [ ] Any approved action has a verified backup, rollback, and post-change verification.
- [ ] Raw task content, private identifiers, credentials, and raw logs are absent from shared evidence; no `kanban tail` or live-follow output was used.
- [ ] Residual uncertainty is a concrete falsifiable question.

## Escalation packet requirements

Provide a redacted, minimal packet containing:

- **Installed version:** exact Hermes version and install method if known.
- **Platform:** OS/version, active profile/home summary, board, interface, and execution backend.
- **Reproduction:** bounded commands, task/run scope, board, assignee, workspace class, and timestamps.
- **Expected behavior:** expected queue, dispatch, worker, run, and terminal state.
- **Actual behavior:** first divergent queue/worker state and structured status/error.
- **Minimal evidence:** stats/list output, named task run plus bounded `hermes kanban log --tail 200 <task-id>` summary using the smallest necessary redacted output, gateway status, bounded gateway log excerpt, and installed-source or official URL.
- **Queue/worker state:** board/task status, dispatcher/gateway status, claim/spawn/liveness, run outcome, heartbeat, and log timestamp relationship.
- **Residual question:** one concrete maintainer question that distinguishes the remaining Hypothesis.
- **Safety record:** read-only probes, explicit approvals, side effects, verified backup, rollback, and post-change verification.
- **Redaction boundary:** redact prompts, task content, paths, profile/session/workspace/task IDs, credentials, endpoints, and raw logs; keep the packet private until reviewed.
