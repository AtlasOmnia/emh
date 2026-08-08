---
name: emh-gateway-diagnostics
description: Use when Hermes gateway messaging fails and service health, adapter authentication, provider inference, routing, or outbound delivery may be confused.
version: 0.2.0
author: Jonathan Rivera
license: UNLICENSED
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [diagnostics, gateway, messaging, delivery, adapters]
    related_skills: [emh-provider-diagnostics, emh-profile-session-skill-diagnostics]
---

# EMH gateway diagnostics

## Overview

Keep gateway service/process health, adapter configuration/authentication, provider inference, session routing, and outbound delivery as separate stages. A healthy gateway process does not prove adapter authentication, inference, routing, or delivery. A provider error after successful ingress does not explain a dead service process.

Evidence priority is explicit: current runtime and installed source outrank generic guidance. The official docs are authoritative current documentation, but qualify gateway and adapter claims against the installed Hermes version, platform, and configured surface.

## When to Use

Use when:

- Hermes receives no message, sends no message, or reports a gateway/adapter delivery failure.
- Service/process health, adapter authentication, provider inference, session routing, or outbound handoff may be the first divergent stage.
- Gateway behavior differs by profile, platform, adapter, or provider route.
- A read-only stage classification is needed before considering restart, re-pairing, token change, provider change, or message resend.

**Don't use for:** provider-only failures reproduced without gateway ingress or delivery; profile/session isolation without routing evidence; Kanban queue/worker incidents; plugin lifecycle; memory; tool registration; interface rendering; environment/backend mismatch; or update recovery. Preserve only the gateway boundary evidence and route the first divergent stage to the owning domain.

## Evidence collection workflow

1. Record **Complaint**; **Vitals**; **Differential diagnosis**; **Confirmed diagnosis**; **Treatment**; **Post-treatment verification**; **Discharge summary or escalation packet** in that order.
2. Capture installed version, platform, active profile/home summary, adapter class, gateway service context, and message/session scope. Redact private identifiers.
3. Check service/process health first with `hermes gateway status`; use bounded gateway logs only as private evidence until redacted.
4. Inspect adapter configuration and authentication as boolean/status facts without printing tokens. Authentication does not prove provider inference.
5. Classify provider inference, selected profile/session route, ingress, and outbound delivery separately. Do not resend a message to reproduce delivery.
6. Record the first divergent stage: before ingress, during adapter handling, during inference, during session routing, or after outbound handoff.
7. Compare one safe status result or existing delivery result only. Any external test, resend, restart, re-pair, credential, provider, or configuration action requires approval.
8. Label every claim exactly as **Observed**, **Reproduced**, **Confirmed in installed source**, **Officially documented**, **Known upstream fix**, or **Hypothesis**.

## Decision tree

1. **Is the gateway service/process healthy?**
   - No: classify service/process health and stop; do not blame delivery or restart automatically.
   - Yes: continue.
2. **Did the adapter receive or authenticate the event?**
   - No: classify adapter/configuration/authentication and do not expose credentials.
   - Yes: continue.
3. **Did provider inference begin and return a result?**
   - No: route provider state or model evidence to `emh-provider-diagnostics`.
   - Yes: continue.
4. **Was the intended profile/session route selected?**
   - No: route isolation/context evidence to `emh-profile-session-skill-diagnostics`.
   - Yes: continue.
5. **Did outbound handoff complete?**
   - No: classify delivery stage, adapter response, and message identifier without replaying the message.
   - Yes: the remaining symptom may be downstream display/recipient behavior; preserve a Hypothesis.
6. **Would the next probe contact an external service or mutate gateway state?**
   - Yes: stop for explicit approval, verified backup, rollback, and post-change verification.
   - No: collect the smallest remaining status fact.

## Exact commands and tool calls

These commands were checked against current Hermes help/source. Run only the smallest relevant subset; gateway output and message metadata remain private until redacted.

### Read-only allowlist

- `hermes --version`
- `hermes status --all`
- `hermes gateway status`
- `hermes auth list`
- `hermes logs list`
- `hermes logs gateway -n 50 --level WARNING`

`hermes auth list` shows credential inventory/status, not raw credentials, but treat all output as private. Do not use `gateway --deep`, a live send, or an external adapter test as an unapproved probe.

### Approval-gated reproductions and mutations

- `hermes gateway start`, `restart`, `stop`, `setup`, `install`, `uninstall`, or enrollment changes service/adapter state.
- Adapter pairing, token changes, provider/model changes, session/profile changes, outbound resend, and external network probes require explicit approval.
- Any bounded delivery test must name the external target, data, expected message, and cleanup/rollback before approval.

Every proposed action requires explicit approval immediately before execution, a verified backup of configuration/credentials where applicable, a rollback procedure, abort condition, and post-change verification. No autonomous repair is permitted.

## Safety and approval boundaries

**Read-only first.** Never silently restart, stop, start, re-pair, enroll, edit adapter configuration, alter tokens, switch providers/models, change routing, resend messages, or contact an external delivery target.

- Separate service/process health, adapter authentication, provider inference, session routing, and outbound delivery.
- Obtain explicit approval for every external probe or mutation; investigation approval is not delivery approval.
- Require a verified backup and credible rollback before configuration, credential, service, routing, or provider changes.
- Redact tokens, private endpoints, message/chat/phone IDs, prompts, recipient content, account identifiers, and raw logs. Keep evidence private.
- A denial, timeout, or external refusal is evidence for that attempt; never silently retry with a broader route.
- After an approved change, verify the same adapter/profile/session, original stage, and delivery result without sending duplicate content.

## Common pitfalls and recovery

- **Pitfall: process health equals delivery success.** Recovery: collect adapter, inference, routing, and outbound stages separately.
- **Pitfall: authentication equals inference.** Recovery: preserve auth status and provider result as distinct facts.
- **Pitfall: wrong profile route is blamed on the gateway.** Recovery: record redacted profile/home/session identity and route selection.
- **Pitfall: replaying a message as a diagnostic shortcut.** Recovery: stop; use existing bounded status/result evidence and obtain approval for any external test.
- **Pitfall: broad raw gateway logs are shared.** Recovery: retain only stage, timestamp, status, and minimal redacted error.
- **Pitfall: a provider error explains a dead process.** Recovery: classify service/process health first and route provider evidence separately.

## Verification checklist

- [ ] Installed version, platform, profile/home, adapter, service context, and message/session scope are recorded.
- [ ] Service/process health, adapter authentication, provider inference, session routing, ingress, and outbound delivery are distinct.
- [ ] Every conclusion has one exact evidence label and adjacent bounded source.
- [ ] No message was replayed and no external target was contacted without explicit approval.
- [ ] No service, adapter, credential, provider, routing, or profile mutation occurred without approval.
- [ ] Any approved action has a verified backup, rollback, and same-stage post-change verification.
- [ ] Credentials, private endpoints, message content/IDs, and raw logs are absent from shared evidence.
- [ ] Residual uncertainty is a falsifiable delivery-stage question.

## Escalation packet requirements

Provide a redacted, minimal packet containing:

- **Installed version:** exact Hermes version and install method if known.
- **Platform:** OS/version, active profile/home summary, adapter, gateway service context, and interface.
- **Reproduction:** bounded status/log commands, message/session scope, time window, and whether any external test was approved.
- **Expected behavior:** expected ingress, inference, routing, handoff, and delivery result.
- **Actual behavior:** first divergent stage and structured status/error.
- **Minimal evidence:** gateway status, auth summary, bounded gateway log excerpt, existing delivery result, and installed-source or official URL.
- **Delivery stage:** service/process, adapter/authentication, ingress, provider inference, session routing, outbound handoff, or recipient acknowledgement classification.
- **Residual question:** one concrete maintainer question that distinguishes the remaining Hypothesis.
- **Safety record:** read-only probes, explicit approvals, external contacts, side effects, verified backup, rollback, and post-change verification.
- **Redaction boundary:** redact tokens, credentials, prompts, message/phone/chat IDs, private endpoints, paths, recipient content, and raw logs; keep the packet private until reviewed.
