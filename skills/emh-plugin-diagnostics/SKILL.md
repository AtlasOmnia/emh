---
name: emh-plugin-diagnostics
description: Use when a Hermes backend plugin or Desktop plugin is missing, registered unexpectedly, or behaves differently at runtime.
version: 0.1.0
author: Jonathan Rivera
license: UNLICENSED
platforms: [linux, macos, windows]
---

# EMH plugin diagnostics

Treat two plugin systems as different systems. Python backend plugins under `$HERMES_HOME/plugins` have manifest, registration, enablement, import, and runtime concerns. Uncompiled JavaScript Desktop plugins under `$HERMES_HOME/desktop-plugins` have Desktop inventory, settings, hot reload, and UI concerns. Backend registration does not imply Desktop UI.

## Workflow

1. Record **Complaint**, **Vitals**, **Differential diagnosis**, **Confirmed diagnosis**, **Treatment**, **Post-treatment verification**, and **Discharge summary or escalation packet** in that order.
2. Inspect the relevant inventory and manifest without exposing private paths. For backend plugins, check registration, enablement, import, and runtime separately. For Desktop plugins, check inventory, Desktop settings, hot-reload state, and UI reachability separately.
3. Compare the observed surface with installed source and current official documentation. Use **Observed**, **Reproduced**, **Confirmed in installed source**, **Officially documented**, **Known upstream fix**, or **Hypothesis** labels.

## Safety boundaries

Do not install, remove, enable, disable, reload, compile, or edit a plugin without explicit approval. Do not treat a backend plugin as a Desktop plugin or vice versa. Do not upload plugin bundles or logs. Redact private paths, credentials, and identifiers.

## Pitfalls

- Assuming backend registration produces a Desktop pane.
- Treating a manifest entry as proof that import or runtime succeeded.
- Using hot reload as a substitute for a fresh-session verification.
- Changing enablement while the symptom is still unclassified.

## Verification

- Backend and Desktop plugin evidence is reported in separate sections.
- Registration, enablement, import/runtime, inventory/settings, hot reload, and UI are not conflated.
- No lifecycle action occurred without approval.
- Verification uses the same surface and profile as the complaint.

Case record labels: Complaint; Vitals; Differential diagnosis; Confirmed diagnosis; Treatment; Post-treatment verification; Discharge summary or escalation packet.

Evidence labels: Observed; Reproduced; Confirmed in installed source; Officially documented; Known upstream fix; Hypothesis.
