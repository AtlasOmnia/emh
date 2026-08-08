# Official source index

This index is a concise routing aid, not a mirror of Hermes documentation. **Officially documented** facts must be checked against the installed version; current docs may describe a newer runtime. **EMH Recommendation** means diagnostic process guidance, not Hermes behavior.

| Subsystem | Official source | Use |
| --- | --- | --- |
| Hermes overview | https://hermes-agent.nousresearch.com/docs | Official entry point and current documentation. |
| Profile distributions | https://hermes-agent.nousresearch.com/docs/user-guide/profile-distributions | Manifest, ownership, install/update contract. |
| Profile commands | https://hermes-agent.nousresearch.com/docs/reference/profile-commands | Current profile and distribution CLI syntax. |
| Profiles | https://hermes-agent.nousresearch.com/docs/user-guide/profiles | Profile identity and isolation. |
| Memory | https://hermes-agent.nousresearch.com/docs/user-guide/features/memory | Built-in memory and optional provider behavior. |
| Kanban | https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban | Queues, claims, dispatch, workers, and runs. |
| Backend plugins | https://hermes-agent.nousresearch.com/docs/user-guide/features/plugins | User-facing plugin behavior and lifecycle. |
| Backend plugin development | https://hermes-agent.nousresearch.com/docs/developer-guide/plugins | Python plugin registration and runtime contract. |
| Desktop plugin SDK | https://hermes-agent.nousresearch.com/docs/developer-guide/desktop-plugin-sdk | Uncompiled JavaScript Desktop plugin surfaces. |
| Messaging and gateways | https://hermes-agent.nousresearch.com/docs/user-guide/messaging/ | Adapter, routing, and outbound delivery behavior. |
| Providers | https://hermes-agent.nousresearch.com/docs/integrations/providers | Provider, model, endpoint, and authentication behavior. |
| Sessions | https://hermes-agent.nousresearch.com/docs/user-guide/sessions | Stored sessions and context behavior. |
| Skills | https://hermes-agent.nousresearch.com/docs/user-guide/features/skills | Skill discovery, frontmatter, and enablement. |
| Tools | https://hermes-agent.nousresearch.com/docs/user-guide/features/tools | Tool registration and availability. |
| Tool runtime internals | https://hermes-agent.nousresearch.com/docs/developer-guide/tools-runtime | Discovery, requirement gates, toolset resolution, schemas, approval/dispatch, handlers, and result shaping. |
| Tool reference | https://hermes-agent.nousresearch.com/docs/reference/tools-reference | Current tool syntax and capabilities. |
| CLI commands | https://hermes-agent.nousresearch.com/docs/reference/cli-commands | Current command syntax and flags. |
| Classic CLI | https://hermes-agent.nousresearch.com/docs/user-guide/cli | CLI routing, `prompt_toolkit`, input, keybindings, and display behavior. |
| Environment | https://hermes-agent.nousresearch.com/docs/reference/environment-variables | Supported environment variables and scope. |
| Configuration and execution backends | https://hermes-agent.nousresearch.com/docs/user-guide/configuration | Current configuration precedence and terminal backend contract. |
| Security and approvals | https://hermes-agent.nousresearch.com/docs/user-guide/security | Approval, isolation, environment, and redaction boundaries. |
| Native Windows | https://hermes-agent.nousresearch.com/docs/user-guide/windows-native | Native Windows runtime, paths, processes, and platform-specific behavior. |
| TUI | https://hermes-agent.nousresearch.com/docs/user-guide/tui | Terminal UI behavior. |
| Desktop | https://hermes-agent.nousresearch.com/docs/user-guide/desktop | Desktop surface and settings behavior. |
| Updating and rollback | https://hermes-agent.nousresearch.com/docs/getting-started/updating | Update stages, backup modes, interruption behavior, validation, and rollback. |
| Official latest release | https://github.com/NousResearch/hermes-agent/releases/latest | Version-matched release notes and upstream fixes. |
| Official release API | https://api.github.com/repos/NousResearch/hermes-agent/releases/latest | Bounded latest-release metadata used by EMH. |

## Evidence discipline

Use these labels exactly: **Observed**, **Reproduced**, **Confirmed in installed source**, **Officially documented**, **Known upstream fix**, and **Hypothesis**. Prefer live runtime evidence, installed source/tests, version-matched release notes, current official docs, and official NousResearch releases/commits/issues/PRs in that order. Community material is explicitly unverified support only.

Cite an official source adjacent to the claim it supports. Compare the installed version with the current official release before applying current docs to an older runtime. A newer release is not automatically necessary and is not a Known upstream fix without version-matched evidence.
