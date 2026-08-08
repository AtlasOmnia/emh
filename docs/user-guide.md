# EMH — A Simple Guide

**EMH (Emergency Medical Hermes)** is a diagnostic assistant for when your Hermes Agent is misbehaving. Think of it as a doctor for your software: it checks what's actually wrong, explains its reasoning, and proposes the smallest safe fix — but it never touches anything without your permission.

---

## What EMH does for you

- **Diagnoses problems** — you describe the symptom, EMH runs safe read-only checks, labels its evidence, and tells you what's most likely wrong and what to check next.
- **Watches your health** — optionally, a nightly 03:00 check sweeps your Hermes setup and tells you if anything needs attention (it never repairs anything itself).
- **Learns from the community** — every week EMH reviews help threads from the Hermes community, verifies the fixes people share, and stores the good ones as evidence-labeled proposals. When you describe a problem later, EMH can use what the community learned.
- **Stays honest** — every claim is labeled: *Observed*, *Confirmed in installed source*, *Hypothesis*, and so on. It tells you what it knows, what it's guessing, and what would prove it wrong.

## Install

```bash
REPO_DIR="$PWD"                                    # where you cloned/downloaded EMH
TEST_HERMES_HOME="$(mktemp -d)"                    # a safe scratch space
HERMES_HOME="$TEST_HERMES_HOME" hermes profile install "$REPO_DIR" --name emh -y
```

> Prefer testing in a disposable Hermes home first. EMH ships no provider keys or credentials — bring your own model setup.

## Use it

```bash
hermes -p emh chat
```

Then just describe the problem like you'd describe symptoms:

> "My Telegram gateway stopped sending messages after I updated."

EMH will run read-only checks, give you a diagnosis with evidence labels, and propose a treatment. **Nothing is changed until you approve it.**

**First time?** Type `setup` to run orientation. EMH will explain the optional nightly health check and update checking, and ask your permission before installing anything.

## The nightly health check (optional)

- Runs daily at 03:00 on your **default profile** (where your notification channels live).
- Checks: core health, stuck sessions, memory, storage, backups, and your scheduled jobs.
- Reports either `All clear.` or a short `ATTENTION NEEDED` list.
- It is **read-only** — it never restarts, prunes, or repairs anything.

## How EMH learns

1. Help threads from the Hermes community are collected weekly.
2. Each thread is scored automatically (was the problem real? did the fix work?).
3. A vetting agent reads the best candidates, checks the commands against your installed Hermes, and writes evidence-labeled proposals.
4. Proposals are reviewed by a human before anything becomes official EMH knowledge.
5. When you triage a problem, EMH can consult that community knowledge as leads — clearly marked as proposals, never as gospel.

Optionally, a weekly **update-check** compares your installed EMH against its source and tells you when a new version is available. It only reports — it never updates itself.

## What EMH will never do

- ❌ Repair, restart, update, or delete anything without your explicit approval.
- ❌ Show or ask for your API keys, tokens, or passwords.
- ❌ Send your data anywhere (no telemetry, no uploads).
- ❌ Claim something is fixed when it hasn't been verified.

## Need help?

- Official Hermes documentation: https://hermes-agent.nousresearch.com/docs
- Ask EMH to re-run vitals if a symptom changes.
- If EMH itself fails to launch, keep the error message — that's your diagnostic packet.
