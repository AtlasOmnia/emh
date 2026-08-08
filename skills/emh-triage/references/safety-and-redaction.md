# Safety and redaction

EMH is a software diagnostic aid. It is not medical care, and its clinical voice never overrides operator consent or evidence.

## Read-only first

Begin with bounded status, version, source, and redaction checks. Do not silently write configuration, alter a profile or home, restart a service, re-pair a gateway, switch a provider or model, request a raw key, edit memory, repair a database, reclaim a task, enable or disable a plugin or skill, upload data, send telemetry, create cron/MCP/plugin state, or perform destructive Git operations.

A proposed update, repair, reset, delete, prune, remove, install, reload, reassign, unblock, or completion action requires explicit approval with scope and expected impact. Back up first for destructive or difficult-to-reverse changes. Preserve a rollback path and define post-treatment verification before acting.

## Redaction list

Before display, persistence, or escalation, redact:

- API keys, bearer tokens, OAuth access or refresh values, passwords, secrets, cookies, session values, and private-key blocks.
- Private URLs, hostnames, ports, filesystem paths, usernames, repository remotes, and environment values.
- Phone numbers, email addresses, chat IDs, account IDs, message IDs, and comparable identifiers.
- Raw logs, incident transcripts, copied memory entries, temporary errors, and speculative diagnoses when they are not required for the claim.

Never ask the operator to paste a raw secret. Request a redacted status, a boolean, a version, a count, or a short structural excerpt instead.

## Memory retention boundary

Persist only stable, non-secret environment facts that improve future diagnosis, such as an OS family, a deliberately supplied Hermes version, or a known installation method. Never persist raw logs, incident transcripts, keys, tokens, cookies, phone or email identifiers, chat IDs, temporary failures, or hypotheses. Do not reset or delete memory as a diagnostic shortcut.

## Safe sharing

An escalation packet is redacted, minimal, GitHub-ready, and limited to versions/install method/platform, reproduction, expected/actual results, minimal evidence, safe-mode differential, installed-source evidence, release comparison, and a precise question. Official facts and EMH Recommendations are separated and cited adjacent to the relevant text.

## Pitfalls

- Assuming a redacted string is safe because it looks like a placeholder.
- Treating a local URL or path as public merely because it has no password.
- Saving the whole terminal transcript when one exit code is sufficient.
- Approving a difficult-to-reverse change without a backup and rollback check.

## Verification

- The diagnostic path is read-only until an explicit approval boundary.
- The proposed change, backup, rollback, and verification checks are stated.
- Shared output contains no raw credentials, private identifiers, private endpoints, or copied logs.
- Retained memory contains stable non-secret facts only.

## Case record

Complaint; Vitals; Differential diagnosis; Confirmed diagnosis; Treatment; Post-treatment verification; Discharge summary or escalation packet.

Evidence labels: Observed; Reproduced; Confirmed in installed source; Officially documented; Known upstream fix; Hypothesis.
