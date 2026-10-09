# Issue template

The one format for ACU code issues. The Linear "Product Work Item" template
mirrors this file; change both together.

```markdown
## Problem
<What happens now, who it hurts, and why it matters. For a bug: observed
versus expected. Two to four sentences.>

## Evidence
**Confirmed:** <what was checked and how: call or interaction ID, log line,
failing test, query result, or code symbol at a commit>
**Unverified:** <claims not yet checked, or "None">

## Change
<The behavior after the work, seen from outside. Name the interfaces, types,
functions, routes, or tools involved by name. Not a step-by-step recipe.>

## Acceptance criteria
- [ ] <One independently testable outcome>
- [ ] <...>

## Verify
<The proof the builder must show; see the table below.>

## Out of scope
- <Adjacent work this issue must not touch>

## Notes
<Optional: links, decisions already made, prior attempts.>
```

## Verify by kind

| Kind | Proof |
|---|---|
| Bug | A test or repro that fails before the change and passes after |
| Feature | Tests at the highest existing boundary covering each criterion |
| Refactor or cleanup | A test or snapshot that records current behavior, unchanged after |
| Performance | A baseline number, a target, and the same measurement after |
| Prompt or agent behavior | An eval scenario that fails before and passes after |

## Rules

- Name symbols and behaviors. A `path:line` is a pointer, stamped with the
  commit it was read at, never the contract.
- Each criterion is checkable by a test, a command, or a record lookup.
  "Works correctly" is not a criterion.
- No patient names, phone numbers, dates of birth, chart numbers, or
  transcripts. Use interaction IDs.
