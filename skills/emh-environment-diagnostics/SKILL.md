---
name: emh-environment-diagnostics
description: Use when Hermes behavior differs by operating system, WSL boundary, host, shell, filesystem, network, process context, or execution backend.
version: 0.2.0
author: Jonathan Rivera
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [diagnostics, environment, platforms, backends, persistence]
    related_skills: [emh-tool-runtime-diagnostics, emh-triage]
---

# EMH environment diagnostics

## Response presentation

Use the shared [EMH response reference](../emh-triage/references/response-templates.md) for normal answers: lead with **What I found**, **What it means**, **Safest next step**, **Permission needed: Yes/No**, then **Technical details**. Preserve this skill's domain workflow, evidence labels, and safety/approval rules; this presentation guidance does not replace them. Keep mutation, external-contact, sensitive-risk, safety, and data-loss warnings in the concise answer, and keep technical proof complete and redacted.

## Overview

Diagnose two environments independently:

- **Host/runtime environment:** macOS, Linux, native Windows, or WSL; Hermes process identity; launch shell; profile/home; filesystem; permissions; environment; host network; and service processes.
- **Execution environment:** the backend used by terminal/file/code tools — local, Docker, SSH, Modal, Daytona, Vercel Sandbox, or Singularity/Apptainer — including its OS, shell, working directory, path mapping, permissions, environment passthrough, network, process namespace, persistence, and artifact location.

Installed source defines one execution-environment interface and selects a backend from terminal configuration. “Local” can affect the host; every other backend has its own lifecycle and persistence contract. WSL is a separate Linux environment with Windows interoperability, not native Windows with slash changes.

Evidence priority is explicit: current runtime and installed source outrank generic guidance. The official docs are authoritative current documentation, but qualify backend behavior against the installed version. Current entry points are https://hermes-agent.nousresearch.com/docs/user-guide/features/tools, https://hermes-agent.nousresearch.com/docs/user-guide/configuration, https://hermes-agent.nousresearch.com/docs/reference/environment-variables, and https://hermes-agent.nousresearch.com/docs/user-guide/windows-native.

## When to Use

Use when:

- A failure reproduces on one OS, WSL/native boundary, user account, shell, service context, or filesystem but not another.
- A terminal/file/code tool sees a different OS, working directory, path, permission, environment, network, process, or artifact than the host.
- Local works but Docker/SSH/Modal/Daytona/Vercel Sandbox/Singularity fails, or the reverse.
- A file/process exists in one backend or session but disappears in another.
- Cross-platform reproduction is needed without silently normalizing away the meaningful difference.

**Don't use for:** a tool missing before backend selection; interface rendering/input alone; provider authentication independent of environment; profile/session/skill discovery without an OS/backend symptom; or update-stage recovery. Preserve relevant evidence and route to those domains.

## Evidence collection workflow

1. Record **Complaint**; **Vitals**; **Differential diagnosis**; **Confirmed diagnosis**; **Treatment**; **Post-treatment verification**; **Discharge summary or escalation packet**.
2. Capture host facts first: installed version, OS family/version, native Windows versus WSL, launch surface, shell/TTY or service context, effective profile/home summary, and host working directory. Redact usernames and paths.
3. Capture execution-backend identity separately from the host. Do not infer backend OS, shell, cwd, permissions, environment, network, process namespace, or persistence from host evidence.
4. Run one fixed backend probe for OS, cwd, PID, and permissions. Record the exact tool call and result status. Do not dump the full environment or process table.
5. Compare path forms and artifact locations: host path, backend path, mount/sync mapping, and the surface/tool that created the artifact. A path string that is valid on the host can be meaningless in the backend.
6. Compare environment by named variable presence or a redacted bounded prefix only. Distinguish inherited, explicitly passed through, backend-generated, and absent values. Never collect all variables.
7. Compare network in three layers: name resolution, route/connectivity, and application/authentication. Any external probe contacts a system and requires approval; a failed connection is not automatically DNS or credential failure.
8. Compare process evidence by backend namespace and ownership. `process(action="list")` covers Hermes-managed background processes, not every host/container process.
9. Establish persistence only with existing artifacts first. Creating a probe file, opening a remote sandbox, installing a package, or deleting cleanup is mutation and requires approval plus a cleanup/rollback plan.
10. Reproduce the same bounded probe across the minimum two environments and change one variable at a time.
11. Label each claim exactly as **Observed**, **Reproduced**, **Confirmed in installed source**, **Officially documented**, **Known upstream fix**, or **Hypothesis**.

## Decision tree

1. **Does host evidence differ before any tool backend runs?**
   - Yes: classify OS/native/WSL, shell/TTY, service user, profile/home, path, permission, or host network.
   - No: continue to execution evidence.
2. **Does the backend report a different OS or shell?**
   - Yes: expected isolation or backend selection; apply that backend's path/command semantics.
   - No: continue.
3. **Is the working directory missing, inaccessible, or mapped elsewhere?**
   - Missing: stale cwd, unmounted workspace, sync failure, or wrong backend.
   - Inaccessible: user/UID/ACL/mode differential.
   - Different path but same artifact: path-mapping difference, not data loss.
4. **Is a named environment value absent only in the backend?**
   - Yes: passthrough/scope differential. Do not copy a secret into the backend as a diagnostic shortcut.
5. **Does name resolution work but connection fail?**
   - Yes: routing, firewall, bind address, proxy, service, or policy differential.
   - No resolution: DNS/backend network configuration differential.
6. **Does a process exist on host but not in backend?**
   - Yes: namespace/lifecycle difference. Verify the owning environment instead of restarting it.
7. **Does an artifact disappear after `/new`, process restart, or backend recreation?**
   - Yes: determine whether the documented persistence scope is process, container/workspace, or external storage. Do not recreate/delete until approved.
8. **Does only one backend fail the same tool handler?**
   - Yes: execution-backend differential; carry tool-runtime evidence into this skill.
   - No: return to the higher tool/interface/provider layer.

## Exact commands and tool calls

These were confirmed in installed help/source or current official documentation. Run only the smallest relevant subset.

### Read-only allowlist

- `hermes --version`
- `hermes status --all`
- `hermes tools list --platform cli`
- `terminal(command="python -c \"import os, platform; print(platform.system(), platform.release()); print(os.getcwd()); print(os.getpid())\"")`
- `terminal(command="python -c \"import os; print(os.access('.', os.R_OK), os.access('.', os.W_OK), os.access('.', os.X_OK))\"")`
- `terminal(command="python -c \"import os; print(os.environ.get('PATH', '').split(os.pathsep)[:5])\"")`
- `process(action="list")`
- `read_file(path="<expected-artifact-path>")`

The `terminal` calls report the execution backend, not necessarily the host. Cwd and PATH fragments are private until redacted. `read_file` is allowed only for a known, non-secret artifact the operator identified; do not scan a home directory or credential path.

### Approval-gated probes and mutations

- Any external DNS, connection, HTTP, provider, SSH, or cloud-sandbox probe contacts another system and requires explicit approval and a named target.
- `terminal(command="python -c \"from pathlib import Path; Path('emh-persistence-probe.txt').write_text('probe', encoding='utf-8')\"")` creates backend state.
- `terminal(command="python -c \"from pathlib import Path; Path('emh-persistence-probe.txt').unlink(missing_ok=True)\"")` deletes backend state.
- Changing terminal backend, cwd, image, mounts, resource limits, environment passthrough, credentials, permissions, firewall, service user, or persistence settings is mutation.
- Starting/recreating/stopping a Docker container, SSH workspace, Modal/Daytona/Vercel sandbox, or Singularity instance is lifecycle mutation even if the test command is read-only.

Before any mutation, record exact backend and target, explicit approval, verified backup where state exists, rollback/cleanup, expected artifact location, and post-change verification. Never use a real user home or production workspace for a persistence probe when an approved disposable location is available.

## Safety and approval boundaries

**Read-only first.** Never silently change backend, cwd, mounts, permissions, ownership, PATH, environment passthrough, network policy, service state, container/workspace lifecycle, or artifacts.

- Obtain explicit approval before external network access, remote/cloud execution, process start/stop, file creation/deletion, install, permission change, or configuration edit.
- Require a verified backup and credible rollback before changing persistent workspaces, mounts, host files, ACLs/modes, service definitions, or backend configuration.
- Do not dump environment variables, process command lines, routing tables, filesystem trees, home directories, credentials, SSH material, or cloud metadata.
- Local backend commands can modify the host. A sandbox label is not proof of isolation, privacy, disposability, or non-persistence.
- Do not copy credentials across host/WSL/container/remote boundaries to make a probe pass.
- Redact hostnames, usernames, IPs, ports, paths, workspace IDs, process arguments, and artifact content before escalation.

## Common pitfalls and recovery

- **Pitfall: reporting host OS as backend OS.** Recovery: run the bounded platform probe through the affected tool and record host/backend facts side by side.
- **Pitfall: treating native Windows and WSL as one filesystem.** Recovery: record which executable launched Hermes, path form, mount translation, and owning environment; reproduce without silently crossing the boundary.
- **Pitfall: assuming local, Docker, or cloud starts fresh each call.** Recovery: identify process/workspace lifecycle and current documented persistence scope before creating or deleting anything.
- **Pitfall: using `env`, recursive listing, or full process output.** Recovery: ask one named question and collect a boolean, count, version, PID, or redacted prefix.
- **Pitfall: diagnosing permissions by writing.** Recovery: use `os.access` plus metadata first; write only in an approved disposable location when metadata cannot answer the question.
- **Pitfall: calling connection refusal an authentication failure.** Recovery: separate resolution, route/connect, service/bind, protocol, and authentication evidence.
- **Pitfall: looking for an artifact on the host when it was created remotely.** Recovery: record the backend-returned cwd/artifact path and any sync/export step.
- **Pitfall: “cleanup” without approval.** Recovery: leave the probe artifact in place, record it as residual state, and obtain approval for deletion.

## Verification checklist

- [ ] Host and execution-backend evidence are in separate sections.
- [ ] macOS/Linux/native Windows/WSL identity and local/Docker/SSH/Modal/Daytona/Vercel Sandbox/Singularity identity are explicit where relevant.
- [ ] OS, shell, cwd/path mapping, permissions, named environment scope, network layers, process namespace, persistence, and artifact location are not conflated.
- [ ] The same bounded probe changed only one environmental variable between reproductions.
- [ ] Every conclusion has one exact evidence label and adjacent bounded source.
- [ ] No environment dump, recursive inventory, credential, private path, process argument list, or raw log is present.
- [ ] Any approved state change has a verified backup, rollback/cleanup, and artifact-location verification.
- [ ] Residual artifacts and remote resources are explicitly listed; none were silently deleted.

## Escalation packet requirements

Provide a redacted, minimal cross-platform packet containing:

- **Installed version:** exact Hermes version and install method if known.
- **Platform:** host OS/version, native/WSL status, launch shell/service context, architecture when relevant, and comparison platform.
- **Execution backend:** local, Docker, SSH, Modal, Daytona, Vercel Sandbox, or Singularity; backend OS/shell; lifecycle; and persistence scope.
- **Reproduction:** identical bounded host/backend probes, tool call, working-directory setup, and one changed variable.
- **Expected behavior:** expected OS/path/permission/environment/network/process/persistence/artifact result.
- **Actual behavior:** first divergent host/backend fact and structured status.
- **Minimal evidence:** redacted versions, cwd/path mapping, permission booleans, named-variable presence, network stage, PID/status, and artifact location; include installed-source symbol or official URL where relevant.
- **Cross-platform matrix:** host versus backend and working versus failing platform/backend in separate columns.
- **Residual question:** one concrete question that distinguishes the remaining Hypotheses.
- **Safety record:** read-only probes, approved network/lifecycle/file actions, verified backup, rollback/cleanup, and residual resources.
- **Redaction boundary:** redact credentials, environment values, usernames, hostnames, addresses, ports, paths, workspace/process IDs, and artifact content. Keep the packet private until reviewed; never attach raw logs, full environment/process dumps, or cloud metadata.
