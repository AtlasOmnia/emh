# Subsystem map

Use this matrix as an EMH Recommendation for choosing the smallest read-only probe. Official command syntax and behavior remain subject to the installed version and the current official source index.

| Symptom | Safe evidence | Likely layer | Approval-gated change |
| --- | --- | --- | --- |
| CLI/TUI/Desktop starts, routes, renders, accepts input, or transports events differently | Version, help/status output, surface-specific reproduction with identity held constant | `emh-interface-diagnostics`: CLI parser/`prompt_toolkit`; TUI Node/TTY/render/input/keybindings/transport; Desktop main/preload/renderer/backend | Edit only the approved surface after verified backup and rollback |
| Wrong profile or home appears active | Profile identity, effective-home summary, process context | Profiles/environment | Change selection or environment only with approval |
| Memory is missing or stale | Built-in MEMORY/USER status, profile scope, session-start snapshot age, optional external-provider status | Memory/profile/provider | Never reset/delete; approve provider or retention change |
| Kanban task is stuck | Queue/task state, dispatcher/gateway status, worker spawn/run/log summaries | Kanban, dispatcher, worker | No reclaim, reassign, unblock, or complete without approval |
| Backend plugin is absent | `$HERMES_HOME/plugins` manifest, registration, enablement, import/runtime status | Backend plugin lifecycle | No install/remove/enable/disable/reload without approval |
| Desktop plugin is absent | `$HERMES_HOME/desktop-plugins` inventory, Desktop settings, hot-reload/UI state | Desktop plugin UI | No install/remove/enable/disable/reload without approval |
| Gateway sends or receives nothing | Service/process status; adapter config/auth status; provider inference; session routing; delivery result | Gateway/messaging | Never restart, re-pair, or edit tokens automatically |
| Provider fails | Configured, reachable, authenticated, requested-model availability, context/runtime, fallback order and limits | Provider/model/endpoint | Never switch provider/model or request raw key automatically |
| Skill is ignored | Discovery/frontmatter/enablement and fresh-session state | Skills/profile/session | No prune/delete/reset/enable/disable without approval |
| Tool is absent, denied, malformed, mis-dispatched, or truncated | Registration, requirement gate, toolset resolution, schema, approval, dispatch, handler/backend, result shape, fresh session | `emh-tool-runtime-diagnostics` | No enable/disable/install/reload/invoke/backend change without approval |
| Update question, interruption, failure, or regression | `source_status.py --offline`, installed path/method/source summary, backup/rollback readiness, lock/process metadata, bounded stage evidence | `emh-update-recovery`; use `emh-release-intelligence` only for read-only release comparison | Never fetch, update, restart, reset, checkout, restore, delete, or roll back automatically |
| Host/platform or execution-backend mismatch | Host OS/runtime and separate backend OS/cwd/path/permission/environment/network/process/persistence/artifact evidence | `emh-environment-diagnostics`: macOS/Linux/native Windows/WSL and local/Docker/SSH/Modal/Daytona/Vercel Sandbox/Singularity | Propose only the smallest approved environment/backend change |

## Interpretation boundaries

Separate queue state from dispatcher/gateway state and worker execution. Separate backend Python plugins from uncompiled JavaScript Desktop plugins; backend registration does not imply Desktop UI. Separate configured, reachable, authenticated, and model-available provider states. A stored session is not the same thing as an active context snapshot, and a discovered skill is not necessarily enabled in a fresh session. For tools, separate registration, availability, toolset scope, model-visible schema, call formation, denial/approval, dispatch, handler/backend execution, and result shaping. For environments, never infer execution-backend identity or artifact location from host evidence. For updates, preserve the first failed stage and keep release comparison read-only.

Case record labels in order: Complaint; Vitals; Differential diagnosis; Confirmed diagnosis; Treatment; Post-treatment verification; Discharge summary or escalation packet.

Evidence labels: Observed; Reproduced; Confirmed in installed source; Officially documented; Known upstream fix; Hypothesis.
