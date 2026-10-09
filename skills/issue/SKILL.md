---
name: issue
description: "Write or fix ACU Linear issues an agent can build with the build skill: one repo, testable criteria, named proof, and a ready-for-agent gate. Use when filing code work in Linear, making an issue agent-ready, or splitting large work into tickets."
---

# Issue

Turn a request into Linear issues that `build` can pick up and finish without
asking anything.

## Use when

- Filing code work in Linear from a request, report, call review, or finding.
- Making an existing issue ready for an agent.
- Splitting a large spec into tickets.

## Repositories

| Repository label | Local checkout |
|---|---|
| `acuity_product` | `~/acuity_product` |
| `abita_s2s` | `~/abita_s2s` |
| `abita_middleware` | `~/amd_middleware` |

## Steps

1. **Gather.** Read the whole source: the request, report, call, finding, or
   existing issue with its comments. Search ACU for the same problem in every
   state, including done and canceled. Prefer no new issue over a duplicate:
   add new evidence to the existing one instead.
   Done when: the source is read and duplicates are ruled out or linked.

2. **Trace.** Find the code path in the owning repo's default branch and name
   the one repository that owns the change. Check whether the behavior already
   exists. Split what you confirmed from what you are told.
   Done when: the owner, the code path, and the confirmed and unverified
   evidence are written down.

3. **Size.** One issue is one PR in one repository. If the work is bigger,
   split it into thin end-to-end slices, each one demoable or testable on its
   own, with blocking links between them and the original as parent. Work
   across repositories gets one issue per repository. A parent holds the
   problem and decisions for people; it gets no Repository label and is never
   marked ready.
   Done when: every issue fits one PR in one repository.

4. **Write** each issue with `references/template.md`. The title says the
   outcome in plain words.
   Done when: every section is filled or marked "None".

5. **Gate.** An issue is ready for an agent only if all of these hold:
   - One Repository label, and it fits one PR.
   - Every acceptance criterion is testable, and Verify names the proof.
   - Evidence is confirmed, or the first criterion is to reproduce it.
   - Out of scope is stated.
   - No decision is waiting on Chase or the practice.
   - No patient data.

   If it passes, add `ready-for-agent` and set status Todo. If a person must
   do it (judgment, access, manual testing), leave the label off and say why
   in Notes. Otherwise leave it in Triage and add a "Missing before ready"
   list to Notes.
   Done when: every issue is ready, assigned to a person, or lists what is
   missing.

6. **File.** Team ACU. Project: the outcome it serves, or `Maintenance`.
   Labels: one of `Bug`, `Improvement`, or `Feature`, and one Repository.
   No assignee unless asked.
   Done when: every issue has an ACU identifier.

## Output

```text
ACU-n  <title>  <repository>  ready | for a person: <why> | missing: <items>
```

## Guardrails

- Read-only on code. This skill writes issues, not fixes.
- Never mark an issue ready to get it moving. A wrong ready label costs a
  failed build.
- Keep patient data out of Linear, even when the source contains it.
