---
name: emh-provider-diagnostics
description: Use when Hermes provider or model behavior requires separating configuration, reachability, authentication, capability, fallback, and privacy.
version: 0.2.0
author: Jonathan Rivera
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [diagnostics, providers, models, endpoints, fallback]
    related_skills: [emh-gateway-diagnostics, emh-environment-diagnostics]
---

# EMH provider diagnostics

## Response presentation

Use the shared [EMH response reference](../emh-triage/references/response-templates.md) for normal answers: lead with **What I found**, **What it means**, **Safest next step**, **Permission needed: Yes/No**, then **Technical details**. Preserve this skill's domain workflow, evidence labels, and safety/approval rules; this presentation guidance does not replace them. Keep mutation, external-contact, sensitive-risk, safety, and data-loss warnings in the concise answer, and keep technical proof complete and redacted.

## Overview

Report provider state as separate facts: configured, reachable, authenticated, requested model available, capable of the requested context, and selected in fallback order. Also distinguish runtime detection, rate limits, endpoint identity, and local endpoint privacy. A configured provider is not necessarily authenticated, and a reachable endpoint is not proof that the requested model can serve the request.

Do not introduce model IDs or direct configuration recipes.

Evidence priority is explicit: current runtime and installed source outrank generic guidance. The official docs are authoritative current documentation, but provider and model behavior must be qualified against the installed version, endpoint, credential pool, and platform.

## Vision routing diagnosis

Use this narrow order when an image request is under review:

1. Image attachment/ingress.
2. Active provider/model and positive vision-capability identification.
3. Native pixels-to-active-model route.
4. Auxiliary text-description route via auxiliary.vision for text-only or unsupported route.
5. Separate `vision_analyze` tool exposure/dispatch path.

Treat `hermes tools enable --platform <platform> vision` as persistent approval-gated config that proves only tool exposure, not native image routing. Acceptance uses a fresh session and a non-sensitive image fixture; ending an OCR loop alone is insufficient. Route missing tool/schema issues to `emh-tool-runtime-diagnostics`. Keep auxiliary provider configuration/authentication/capability/fallback/destination privacy distinct.

Evidence priority is explicit: current runtime and installed source outrank generic guidance. The official docs are authoritative current documentation, but provider and model behavior must be qualified against the installed version, endpoint, credential pool, and platform.

## When to Use

Use when:

- Provider or model behavior fails, changes, times out, or falls back unexpectedly.
- Configuration, reachability, authentication, capability, context length, runtime detection, endpoint identity, rate limits, or fallback exhaustion may be confused.
- Local-versus-cloud routing or local endpoint privacy needs an evidence-first classification.
- A provider state report is needed before considering provider/model, endpoint, credential, or fallback changes.

**Don't use for:** gateway service, adapter, ingress, or outbound delivery failures without provider evidence; profile/session isolation; plugin lifecycle; Kanban queue/worker behavior; memory; interface rendering; tool registration; environment/backend mismatch without provider symptoms; or update recovery. Preserve provider evidence and route the first divergent gateway or environment stage to its domain skill.

## Evidence collection workflow

1. Record **Complaint**; **Vitals**; **Differential diagnosis**; **Confirmed diagnosis**; **Treatment**; **Post-treatment verification**; **Discharge summary or escalation packet** in that order.
2. Capture installed version, platform, active profile/home summary, provider class, endpoint identity class, requested model class, and local/cloud route. Redact private details.
3. Run configuration/status reads first. Do not print keys, full URLs, prompts, message content, or resolved private defaults.
4. Report configured, reachable, authenticated, model-available, capable, and selected/fallback state separately. A network response may be a reachability fact without being an inference success.
5. Consider context length, runtime detection, rate limits, endpoint protocol, credential-pool exhaustion, model capability, and fallback order without sending an unapproved test request.
6. Distinguish local endpoint privacy from cloud endpoint privacy. “Local” is a route classification, not proof of safe data handling.
7. If an approved provider-affecting change occurs, repeat the original bounded reproduction and verify endpoint identity, model selection, fallback, privacy route, and residual state.
8. Label every claim exactly as **Observed**, **Reproduced**, **Confirmed in installed source**, **Officially documented**, **Known upstream fix**, or **Hypothesis**.

## Decision tree

1. **Is the intended provider configured?**
   - No: classify configuration and profile scope; do not add a provider as a probe.
   - Yes: continue.
2. **Is the endpoint reachable?**
   - No: classify DNS/network/service/endpoint identity before authentication.
   - Yes: continue.
3. **Is authentication valid without exposing credentials?**
   - No: classify credential pool/auth state; do not request or print a raw key.
   - Yes: continue.
4. **Is the requested model available and capable of the context/runtime?**
   - No: classify model capability, context length, runtime detection, or endpoint mismatch.
   - Yes: continue.
5. **Did fallback select another provider/model or exhaust credentials/rate limits?**
   - Yes: record fallback order and exhaustion; do not silently switch it.
   - No: continue.
6. **Would the next probe contact a provider or change endpoint/model/credential/fallback state?**
   - Yes: stop for explicit approval, verified backup, rollback, and post-change verification.
   - No: collect the smallest remaining read-only fact.

## Exact commands and tool calls

These commands were checked against current Hermes help/source. Run only the smallest relevant subset; provider status and logs remain private until redacted.

### Read-only allowlist

- `hermes --version`
- `hermes status --all`
- `hermes auth list`
- `hermes config check`
- `hermes logs agent -n 50 --level WARNING`

These commands do not authorize an inference request. `hermes auth list` is an inventory/status read but must be treated as private evidence; `hermes config check` must not be treated as proof that a provider is reachable or authenticated.

### Approval-gated reproductions and mutations

- Any provider/model inference request, endpoint health request, or external network probe contacts a provider and requires explicit approval with a named target and data boundary.
- `hermes tools enable --platform <platform> vision` is persistent approval-gated config and proves only tool exposure, not native image routing.
- Provider/model selection, endpoint configuration, credential add/remove/reset/logout, fallback order, privacy route, and profile configuration changes are mutations.
- Credential installation, refresh, or raw-key inspection is never an autonomous diagnostic step.

Every proposed action requires explicit approval, a verified backup of configuration/credential state where applicable, a rollback procedure, abort condition, and post-change verification. Never silently mutate provider or routing state or continue after an abort condition; no autonomous repair is permitted.

## Safety and approval boundaries

**Read-only first.** Never silently switch provider/model, edit endpoint configuration, change fallback order, add/remove/reset credentials, send prompts, upload data, or alter privacy routing.

- Obtain explicit approval before every provider contact, inference request, credential action, or privacy-affecting change.
- Obtain explicit approval before an image is sent to an external auxiliary provider.
- Require a verified backup and credible rollback before changing persistent provider/configuration/fallback state.
- Do not equate configured with authenticated, reachable with capable, local with private, or a newer model with a Known upstream fix.
- Redact credentials, private URLs, prompts, message content, account IDs, request IDs, endpoint headers, and raw logs. Keep provider evidence private.
- A timeout, rate limit, denial, or provider refusal is evidence for that attempt; never silently retry on another provider or model.
- After an approved change, verify the same request class, endpoint identity, model, fallback state, and local/cloud privacy route.

## Common pitfalls and recovery

- **Pitfall: configured means authenticated.** Recovery: report configuration and auth status separately without requesting a raw key.
- **Pitfall: reachable means requested model exists.** Recovery: classify model availability, capability, context length, and endpoint identity separately.
- **Pitfall: fallback hides exhaustion.** Recovery: record credential/fallback order, rate-limit state, and selected provider without changing it.
- **Pitfall: local endpoint means safe data handling.** Recovery: identify actual route, process, storage, and privacy boundary.
- **Pitfall: a generic provider error explains a dead gateway.** Recovery: route service/adapter evidence to gateway diagnostics.
- **Pitfall: sending a live prompt as a probe.** Recovery: preserve status/config evidence and obtain explicit approval for a bounded external test.

## Verification checklist

- [ ] Installed version, platform, profile/home, provider, endpoint class, model class, and local/cloud route are recorded.
- [ ] Configured, reachable, authenticated, available, capable, selected, fallback, rate-limit, and runtime states are separate.
- [ ] Context length, endpoint identity, privacy implications, and credential exhaustion are considered.
- [ ] Every conclusion has one exact evidence label and adjacent bounded source.
- [ ] No provider contact, prompt send, credential, endpoint, model, fallback, or privacy mutation occurred without approval.
- [ ] Any approved action has a verified backup, rollback, and post-change reproduction.
- [ ] Credentials, prompts, private URLs, message content, identifiers, and raw logs are absent from shared evidence.
- [ ] Residual uncertainty is a falsifiable provider-state question.

## Escalation packet requirements

Provide a redacted, minimal packet containing:

- **Installed version:** exact Hermes version and install method if known.
- **Platform:** OS/version, active profile/home summary, interface, provider class, and execution backend.
- **Reproduction:** bounded status/config commands, request class, model class, endpoint class, time window, and approval state for any provider contact.
- **Expected behavior:** expected configured/reachable/authenticated/model/capability/fallback state and privacy route.
- **Actual behavior:** first divergent provider state and structured status/error.
- **Minimal evidence:** version, auth/config summary, bounded log excerpt, endpoint/model class, fallback/rate-limit state, and installed-source or official URL.
- **Provider state:** configured, reachable, authenticated, model availability/capability, context/runtime, endpoint identity, rate limits, fallback selection/exhaustion, and local/cloud privacy classification.
- **Residual question:** one concrete maintainer question that distinguishes the remaining Hypothesis.
- **Safety record:** read-only probes, provider contacts, explicit approvals, side effects, verified backup, rollback, and post-change verification.
- **Redaction boundary:** redact credentials, private URLs, prompts, message content, headers, account/request IDs, and raw logs; keep the packet private until reviewed.
