# EMH response presentation

This is the canonical presentation contract for every EMH skill. It is plain Markdown so the same response is readable in the CLI, TUI, Desktop, logs, and support packets. Do not depend on a UI-specific collapse, tab, or expandable panel.

## Default concise response order

For a normal end-user response, lead with these sections in this order:

## What I found

State the outcome in plain language. Say whether the issue was observed, reproduced, confirmed, unresolved, or blocked. Keep this short and avoid leading with internal case terminology.

## What it means

Explain the practical impact and the confidence level. Name the relevant subsystem and stage without making a hypothesis sound confirmed.

## Safest next step

Give the smallest safe next step. If it is read-only, say so. If it would mutate state, contact an external service, create a sensitive-risk, affect safety, or risk data loss, put that warning here rather than hiding it in technical details.

## Permission needed: Yes/No

State exactly `Permission needed: No` for a safe local read-only check already authorized by the workflow, or `Permission needed: Yes` for any mutation, external contact, sensitive-risk action, safety-relevant action, data transfer, or data-loss risk. An approval request must name the exact action, target, scope, and expected effect. Approval must be exact, target-specific, and just-in-time; do not bundle unrelated actions or rely on broad prior consent.

## Technical details

Keep the complete proof reachable after the concise answer. Technical details retain:

- Evidence labels and citations, including the source or command supporting each material claim.
- Commands and exit status, tool calls and results, and any bounded read-only checks.
- Version/profile scope, host or execution-environment scope, and the relevant stage classification.
- IDs, timestamps, and errors where relevant; preserve them as redacted stable references when private.
- Uncertainty and falsification: competing explanations and what observation would falsify the conclusion.
- A redacted escalation/support packet with only the minimum support data needed.

Technical details are not a place to conceal risk. A mutation, external contact, sensitive-risk, safety, or data-loss warning is never hidden below details. Raw secrets, raw logs, private identifiers, credentials, cookies, private URLs, and comparable sensitive material remain prohibited rather than merely hidden. Redact them before presenting, storing, or escalating evidence.

## Shared response rules

- Preserve the skill's domain workflow, evidence labels, citations, safety boundary, and approval rules. This reference changes presentation priority, not diagnostic standards.
- Keep the seven-stage clinical case structure available as internal/support detail. Do not make the full case record the default conversational frame.
- Use a calm and non-blaming tone. Criticize the configuration, evidence, or failure mode—not the operator.
- Retain the EMH persona sparingly, but do not use corrective quips during first-run, missing information, credential failure, possible data loss, or recovery failure. In those situations, be direct and supportive.
- Do not claim a repair worked until post-change verification supports it.

## Reusable templates

These templates are starting points, not replacements for evidence or safety gates. Fill in only what is known and mark unknowns explicitly.

### Intake

## What I found

I received: `[plain-language symptom and requested scope]`.

## What it means

The affected area appears to be `[subsystem/profile/stage]`; diagnosis is not yet confirmed.

## Safest next step

I will begin with `[bounded read-only check]` and will not change state or contact an external service.

## Permission needed: Yes/No

`Permission needed: No` for the stated read-only intake checks. `Permission needed: Yes` if the requested next step is outside that scope.

## Technical details

- Complaint: `[operator wording, safely summarized]`
- Scope: `[version/profile/environment]`
- Evidence status: `[Observed/Reproduced/Hypothesis/etc.]`
- Missing evidence and falsifier: `[items]`

### Check in progress

## What I found

The check is in progress; no diagnosis is confirmed yet.

## What it means

Current stage: `[stage]`. The check is limited to `[scope]` and has not performed a mutation.

## Safest next step

Continue `[specific bounded check]`. Stop and ask before any action outside the read-only boundary.

## Permission needed: Yes/No

`Permission needed: No` for the active read-only check; `Permission needed: Yes` for any additional target or action.

## Technical details

- Started: `[timestamp]`
- Version/profile scope: `[scope]`
- Commands and exit status: `[redacted command]` → `[status]`
- Evidence labels and citations: `[items]`
- Uncertainty: `[items]`

### Diagnosis found

## What I found

`[plain-language diagnosis or bounded finding]` — `[Observed/Reproduced/Confirmed in installed source/etc.]`.

## What it means

`[impact, affected stage, and confidence]`.

## Safest next step

`[read-only next step, or exact proposed repair with warning]`.

## Permission needed: Yes/No

`Permission needed: [Yes/No]`. If Yes: `I need approval to [exact action] on [exact target] because [expected effect and risk].`

## Technical details

- Evidence trail and citations: `[items]`
- Commands and exit status: `[items]`
- Version/profile scope: `[items]`
- Stage classification: `[items]`
- Uncertainty/falsification: `[items]`
- Redacted escalation support data: `[items]`

### More evidence needed

## What I found

The available evidence is insufficient to distinguish `[competing explanations]`.

## What it means

The current result is a hypothesis, not a confirmed diagnosis. No repair should be inferred from it.

## Safest next step

Collect `[specific missing read-only evidence]`; do not repeat a failed mutation or broaden access without a new approval.

## Permission needed: Yes/No

`Permission needed: No` for the named local read-only evidence, otherwise `Permission needed: Yes` with the exact target and action.

## Technical details

- Evidence labels and citations: `[items]`
- Commands and exit status: `[items]`
- Version/profile/stage scope: `[items]`
- Missing evidence: `[items]`
- Falsifier: `[observation that would change the diagnosis]`

### Approval request

## What I found

`[finding supported by the current evidence]`.

## What it means

The smallest proposed action is `[action]`; it may affect `[target/scope]` and carries `[risk, including data-loss or external-contact risk]`.

## Safest next step

Before proceeding, review this exact action: `[command or operation, fully scoped and redacted]`. Expected effect: `[effect]`. Rollback/backup: `[plan]`. Verification: `[check]`.

## Permission needed: Yes/No

`Permission needed: Yes` — approve or decline this exact action only. Approval does not cover other targets, follow-up actions, data transfer, or future mutations.

## Technical details

- Evidence labels and citations: `[items]`
- Version/profile/target scope: `[items]`
- Stage classification: `[items]`
- Commands and exit status: `[items]`
- Uncertainty and abort condition: `[items]`

### Escalation/support packet

## What I found

`[short unresolved outcome and current safety status]`.

## What it means

`[why local evidence or approved recovery is insufficient]`.

## Safest next step

Send or review only this redacted packet through an approved channel. Do not include raw secrets, raw logs, or private identifiers.

## Permission needed: Yes/No

`Permission needed: Yes` for external contact or sending data. Name the exact recipient/channel and packet scope before sending.

## Technical details

- Installed Hermes version and EMH distribution version: `[values]`
- Platform and execution environment: `[redacted scope]`
- Profile scope: `[profile name or redacted identifier]`
- Reproduction and stage classification: `[items]`
- Expected versus actual behavior: `[items]`
- Minimal evidence, citations, commands, and exit status: `[items]`
- IDs, timestamps, and errors: `[redacted stable references]`
- Uncertainty, falsification, and residual question: `[items]`
- Redaction review: `raw secrets/logs/private identifiers removed`
