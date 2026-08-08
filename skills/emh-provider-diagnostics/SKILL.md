---
name: emh-provider-diagnostics
description: Use when Hermes provider or model behavior requires separating configuration, reachability, authentication, capability, fallback, and privacy.
version: 0.1.0
author: Jonathan Rivera
license: UNLICENSED
platforms: [linux, macos, windows]
---

# EMH provider diagnostics

Report provider state as separate facts: configured, reachable, authenticated, and requested model available. Also check context length, runtime detection, fallback order and exhaustion, rate limits, endpoint identity, and local-versus-cloud privacy.

## Workflow

1. Record **Complaint**, **Vitals**, **Differential diagnosis**, **Confirmed diagnosis**, **Treatment**, **Post-treatment verification**, and **Discharge summary or escalation packet** in that order.
2. Inspect the configured provider and endpoint identity without printing keys. Test reachability only with a bounded, read-only status or inference diagnostic approved for the environment; do not assume reachability means authentication.
3. Determine whether the requested model is available, whether context length or runtime constraints apply, and whether fallback order, exhaustion, or rate limits explain the result.
4. Distinguish local endpoint privacy from cloud endpoint privacy. Label claims **Observed**, **Reproduced**, **Confirmed in installed source**, **Officially documented**, **Known upstream fix**, or **Hypothesis**.

## Safety boundaries

Never switch provider/model, edit endpoint configuration, change fallback order, or request a raw key automatically. Do not include credentials, private URLs, prompts, or message content in evidence. Explicit approval is required for any provider or privacy-affecting change.

## Pitfalls

- Calling a configured provider authenticated.
- Calling a reachable endpoint proof that the requested model exists.
- Hiding fallback exhaustion behind a generic provider failure.
- Equating a local endpoint with safe data handling without checking the route.

## Verification

- Configured, reachable, authenticated, and model-available states are reported separately.
- Context/runtime constraints, fallback state, and rate limits are considered.
- Endpoint identity and privacy implications are stated without private details.
- No provider, model, key, or fallback mutation occurred.

Case record labels: Complaint; Vitals; Differential diagnosis; Confirmed diagnosis; Treatment; Post-treatment verification; Discharge summary or escalation packet.

Evidence labels: Observed; Reproduced; Confirmed in installed source; Officially documented; Known upstream fix; Hypothesis.
