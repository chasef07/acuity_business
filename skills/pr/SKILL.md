---
name: pr
description: "Write a pull request title and body: problem, summary, evidence, product principles, and risk, with before-and-after proof. Use whenever opening or updating a PR, including from build and reflect."
---

# PR

Write a PR a reviewer can judge in two minutes: why, what, proof, and risk.

## Title

`<type>(optional-scope): <summary>` using Conventional Commits: `feat`, `fix`,
`refactor`, `test`, `docs`, `chore`, `perf`, `build`, `ci`, or `revert`. Add
`!` for a breaking change. A squash merge turns the title into the commit
message, so it must describe the whole diff.

## Body

```markdown
## Problem

<What was wrong or missing, from the clinic, patient, or operator's view.>

Fixes ACU-<n>

## Summary

<The smallest view that makes the change clear, then what changed, why, and
which boundary owns it.>

Not changed: <what a reviewer might assume changed but did not>

## Evidence

- Before: <the exact test or reproduction failing on the base branch>
- After: <the same check passing>
- Checks: <commands run and their results>

## Product Principles

- Simplicity: <what was removed, reused, or kept small>
- Craft: <the details handled: names, states, errors, edge cases>
- Failure analysis: <the root cause, and how failure stays visible and recoverable>

## Risk

- Door: one-way | two-way
- Blast radius: <what could break if this is wrong>
- Not verified: <what was not checked, or "none identified">
```

## Rules

- Skip preambles. Use short sentences and plain words.
- **Summary view:** pick the smallest view that makes the key point clear:
  pseudocode, a call tree, a component tree, a file tree, a Mermaid diagram, or
  a `diff` of any of these showing what changed. Usually one is enough.
- **Evidence tiers:** a screenshot or call recording is S-tier for visible
  behavior. Test output is A-tier: show the exact test that now fails and
  passes. A claim with neither goes under `Not verified`.
- **Product Principles:** address only the principles this change materially
  touches. Drop the others.
- Keep the headings. Drop a line inside them when it would say nothing, such as
  `Fixes` with no Linear issue or `Not changed` with nothing worth naming.
- A one-way door is hard to undo: data migrations, deletions, schema changes,
  messages sent to clinics or patients. A two-way door reverts cleanly.
- Open review findings go in one line above `Problem`, only when they exist.
- When updating a PR, rewrite the body to match the final diff. Do not append
  a change log.
- Keep credentials, tokens, patient data, raw transcripts, and private URLs out
  of the PR, including screenshots.

Done when: the title describes the whole diff and every claim in the body
points at evidence.
