# Evidence and source policy

This is the portable evidence contract for EMH. It is a recommendation for organizing diagnostics, not a replacement for Hermes documentation.

## Exact evidence labels

Use only these labels:

- **Observed** — present in the live runtime or supplied redacted output.
- **Reproduced** — the symptom was recreated with a bounded, safe procedure.
- **Confirmed in installed source** — the installed source or tests show the behavior.
- **Officially documented** — stated in current official Hermes documentation for the relevant feature.
- **Known upstream fix** — an official, version-matched release note, commit, issue, or pull request identifies the fix.
- **Hypothesis** — plausible but not yet confirmed.

A recommendation must be marked **EMH Recommendation** and must not be presented as Officially documented behavior.

## Evidence priority and adjacent citations

Prefer, in order: live runtime evidence; installed source and tests; version-matched release notes; current official docs; official NousResearch releases, commits, issues, and pull requests; community reports only when explicitly marked unverified. Put the URL, command, source symbol, or release identifier adjacent to the claim it supports. Do not make one citation silently support unrelated claims.

First obtain installed version, install method, source path summary, and Git state when available. Compare that installed version with the current official release. Use current docs for an old runtime only after documenting the mismatch and qualifying the claim.

## Installed-versus-current matrix

| Question | Installed evidence | Current official evidence | Safe conclusion |
| --- | --- | --- | --- |
| What is running? | Runtime version and bounded vitals | Not required | Observed or Reproduced |
| What should it do? | Installed source/tests | Version-matched docs | Confirm only when they agree |
| Is this fixed upstream? | Current install lacks or has behavior | Version-matched release/commit/issue | Known upstream fix only with both sides identified |
| Should it be changed? | Scope, reversibility, backup | Current documented procedure | EMH Recommendation pending approval |

## Known upstream fix criteria

Use **Known upstream fix** only when an official source identifies the behavior and the release or commit containing the fix is version-matched or explicitly bounded. A newer release existing is not itself a fix, and a community workaround is not an upstream fix. Do not fetch or apply an update automatically.

## GitHub-ready escalation template

```text
Title: <short symptom, no private identifiers>

Versions/install method/platform:
- Hermes version: <version>
- Install method: <method>
- Platform: <OS family/version, if safe>
- Profile/home: <redacted scope summary only>

Complaint:
<minimal symptom and impact>

Reproduction:
<bounded read-only steps>

Expected / actual:
<one comparison>

Evidence:
- Observed: <minimal redacted output>
- Reproduced: <result>
- Confirmed in installed source: <symbol/file summary, no private path>
- Officially documented: <adjacent official URL>
- Known upstream fix: <official release/commit, or not established>
- Hypothesis: <remaining differential>

Safe-mode differential:
<what changed with documented safe mode, if tested>

Question:
<one concrete maintainer question>
```

Remove keys, bearer/OAuth values, passwords, cookies, private URLs and paths, phone numbers, email addresses, chat IDs, raw logs, and local identifiers before sharing.
