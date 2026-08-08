---
name: emh-kanban-diagnostics
description: Use when Kanban queue, dispatcher, gateway, worker spawn, run, or log state appears stuck or inconsistent.
version: 0.1.0
author: Jonathan Rivera
license: UNLICENSED
platforms: [linux, macos, windows]
---

# EMH Kanban diagnostics

Separate queue/task state from dispatcher or gateway state and from worker spawn, run, and log failures. Keep board, assignee, workspace, and profile boundaries explicit.

## Workflow

1. Use **Complaint**, **Vitals**, **Differential diagnosis**, **Confirmed diagnosis**, **Treatment**, **Post-treatment verification**, and **Discharge summary or escalation packet** in that order.
2. Capture read-only board and queue statistics, task state, assignee, workspace, and profile scope. Do not infer a worker failure from a queue count alone.
3. Inspect dispatcher/gateway status separately from worker spawn status, run status, and bounded log summaries. Match task, worker, workspace, and profile identifiers only in redacted form.
4. Distinguish queued, claimed, dispatched, spawned, running, failed, and completed states. Label every claim **Observed**, **Reproduced**, **Confirmed in installed source**, **Officially documented**, **Known upstream fix**, or **Hypothesis**.

## Safety boundaries

Diagnostics are read-only. Do not repair a board, reclaim, reassign, unblock, cancel, or complete a task, restart a dispatcher or gateway, or alter a worker workspace without explicit approval and a backup when applicable. Do not copy raw logs or private identifiers into memory or escalation.

## Pitfalls

- Treating a task queue state as proof of dispatcher health.
- Mixing boards, assignees, workspaces, or profiles.
- Reading a stale worker log as a current run result.
- Reclaiming a task before identifying whether the worker actually spawned.

## Verification

- Queue, dispatcher/gateway, and worker evidence are separate.
- Board, assignee, workspace, and profile boundaries are recorded.
- No task or service mutation occurred.
- Any treatment proposal is approval-gated and has post-treatment verification.

Case record labels: Complaint; Vitals; Differential diagnosis; Confirmed diagnosis; Treatment; Post-treatment verification; Discharge summary or escalation packet.

Evidence labels: Observed; Reproduced; Confirmed in installed source; Officially documented; Known upstream fix; Hypothesis.
