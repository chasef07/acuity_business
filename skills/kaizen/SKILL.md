---
name: kaizen
description: "Weekly audit of acuity_product, abita_s2s, and amd_middleware for bugs, duplication, deletable code, and performance, filed as at most five Linear issues. Use when the weekly kaizen run fires, or when asked to audit, deslop, or find cleanup work across the codebase."
---

# Kaizen

Each week, find the strongest few ways to make the code smaller, simpler,
faster, or correct, and file them in Linear so they get fixed.

## Use when

- The weekend scheduled run fires.
- Asked to audit or deslop the codebase, or to find cleanup work.

## Steps

1. **Scope.** Run:

   ```bash
   ~/acuity_business/skills/kaizen/scripts/scope.py --out <scratchpad>/kaizen-YYYY-MM-DD
   ```

   It fetches each repo, exports its default branch (your checkouts are never
   touched), and writes `scope.json`: the 15 most-changed source files from
   the last 7 days, plus one rotating module per repo chosen by ISO week.
   Done when: the script exits 0 and prints the `scope.json` path.

2. **Fan out.** Start four fresh read-only subagents in parallel, one per
   lens: `bugs`, `duplication`, `deletion`, `performance`. Give each
   `references/reviewer-brief.md` filled with its lens rules, the scope from
   `scope.json` (each repo's `root`, `checkout`, `sha`, and file lists), and
   `{OUT}` = `<scratchpad>/kaizen-YYYY-MM-DD/findings-<lens>.json`.
   Done when: each lens has a findings file, or its reviewer is reported as
   `FAILED`.

3. **Verify.** Open the code for every finding and confirm the quote, the
   line, and the trace yourself. Reviewers misread callers and miss upstream
   validation. Drop anything that does not hold, anything that matches a
   pattern the repo documents on purpose, and anything that would remove a
   safety check without a replacement.
   Done when: every finding is marked `verified` or `rejected` with one line why.

4. **Remove duplicates against Linear.** Each finding's fingerprint is
   `kaizen:<repo>/<path>#<symbol>/<lens>`. List ACU issues labelled `Kaizen`
   in every state, including done and canceled. Drop a finding whose
   fingerprint, or the same symbol and problem, is already open, done, or
   canceled. A canceled issue means "we decided no"; never refile it.
   Done when: every verified finding is `new` or `duplicate of ACU-n`.

5. **Pick at most five.** Rank the new findings: confirmed bugs first, then
   the largest safe deletions and deduplications, then performance findings
   with the strongest evidence. Prefer one structural change over several
   small ones in the same place. Fewer than five, or zero, is a valid week.
   Done when: the picked list is final.

6. **File.** Write each pick with the `issue` skill's template
   (`~/acuity_business/skills/issue/references/template.md`) and file it in
   ACU, project `Maintenance`. Labels: `Kaizen`, the Repository label
   (`acuity_product`, `abita_s2s`, or `abita_middleware` for amd_middleware),
   and `Bug` or `Improvement`. Priority is High for a confirmed bug and Medium
   otherwise. No assignee. A verified finding passes that skill's gate, so add
   `ready-for-agent` and set status Todo; if one does not, file it without the
   label and list what is missing.
   Done when: every pick has an ACU identifier.

7. **Post** the digest to Slack `#product` (`C0C0KP8707R`).
   Done when: the message link is in the reply.

## Issue fields

Fill the `issue` template from the finding:

- **Problem:** what is wrong and why it matters.
- **Evidence:** Confirmed is the quoted code and trace, with
  `<repo>/<path>:<line>` at the short commit; Unverified is "None".
- **Change:** the change and its estimate (`<lines_delta>` lines).
- **Acceptance criteria:** the behavior that must hold after the change.
- **Verify:** the finding's `verify`.
- **Out of scope:** anything nearby the fix must not touch.
- **Notes:** end with
  `kaizen:<repo>/<path>#<symbol>/<lens> · week <n> · <repo>@<short sha>`.

## Digest

```markdown
*Kaizen week <n>*: <k> issues filed, <est. net lines> lines
- <ACU-n> <title> (<lens>, <repo>)

Scope: <repo>: <area> + <n> hot files, for each repo
Dismissed: <count verified-but-not-picked>, <count rejected>, <count duplicates>
<one line per rejected finding a human might disagree with>
```

A week with nothing filed posts the scope and "Nothing worth filing."

## Guardrails

- Read-only on code. Never edit, commit, or push in any repo; fixes go
  through `build` from the Linear issue.
- Never refile a canceled `Kaizen` issue.
- At most five issues per run, across all three repos.
- No patient data, phone numbers, or secrets in issues or Slack, even when they
  appear in test fixtures.
- A finding without quoted code and a trace is `UNKNOWN`, not an issue.
