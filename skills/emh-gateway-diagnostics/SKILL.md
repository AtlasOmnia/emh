---
name: emh-gateway-diagnostics
description: Use when Hermes gateway messaging fails and service health, adapter auth, inference, routing, or outbound delivery may be confused.
version: 0.1.0
author: Jonathan Rivera
license: UNLICENSED
platforms: [linux, macos, windows]
---

# EMH gateway diagnostics

Keep five layers separate: service/process health, adapter configuration and authentication, provider inference, session routing, and outbound delivery.

## Workflow

1. Use **Complaint**, **Vitals**, **Differential diagnosis**, **Confirmed diagnosis**, **Treatment**, **Post-treatment verification**, and **Discharge summary or escalation packet** in exactly that order.
2. Inspect gateway service/process status and safe, bounded logs first. Then inspect adapter configuration/auth status without printing tokens, provider inference, the selected session/profile route, and the final outbound delivery result.
3. Reproduce with a safe status or test path when available. Label claims **Observed**, **Reproduced**, **Confirmed in installed source**, **Officially documented**, **Known upstream fix**, or **Hypothesis** and cite adjacent official material.
4. State whether the failure is before ingress, during inference, during session routing, or after outbound handoff. Do not use a provider error to explain a dead service process without evidence.

## Safety boundaries

Never restart, re-pair, edit adapter configuration, alter tokens, switch providers/models, or resend outbound messages automatically. Redact auth, private endpoints, message IDs, phone numbers, and chat IDs. Obtain explicit approval and a rollback plan for any change.

## Pitfalls

- Equating process health with delivery success.
- Equating adapter authentication with provider inference.
- Routing a session from the wrong profile and blaming the gateway.
- Replaying a message as a diagnostic shortcut.

## Verification

- Service, adapter, provider, session, and delivery evidence are distinct.
- Credentials and private message identifiers are absent from evidence.
- The safe read-only probe and exit/result status are recorded.
- Any treatment has explicit approval and post-treatment delivery verification.

Case record labels: Complaint; Vitals; Differential diagnosis; Confirmed diagnosis; Treatment; Post-treatment verification; Discharge summary or escalation packet.

Evidence labels: Observed; Reproduced; Confirmed in installed source; Officially documented; Known upstream fix; Hypothesis.
