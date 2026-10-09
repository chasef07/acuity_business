---
name: build
description: "Build a feature or fix in one repository: scope it from the evidence and current code, build test-first, then loop with a fresh reviewer for bugs, simplicity, and scope. Use when asked to build, implement, or fix something."
---

# Build

Make the change as small as possible, prove it works, and get fresh eyes on it
before anyone else does.

## Use when

- Building a feature or fixing a bug in one repository.

## Not for

- Work across several repositories or workstreams. Use the `orchestrator`
  skill.

## Steps

1. **Scope.** Read the evidence (the request, a failing test, log, call, or
   report) and trace the code path the change touches. Write two lines: what
   will change, and what will not.
   Given a Linear issue, read it with its comments: its Change, Acceptance
   criteria, Verify, and Out of scope are the scope.
   Done when: the scope is written.

2. **Build.** Work on a branch, test first: write a test that fails for the
   reason in the scope, then the least code that makes it pass, one slice at a
   time. Use subagents only for independent changes in different files. Note
   problems outside the scope; do not fix them. Leave cleanup to review.
   Done when: the new test passes, and fails without the change.

3. **Verify.** Run the repository's checks. "It compiles" is not proof.
   Done when: checks pass and the before-and-after proof is captured.

4. **Review.** Start a fresh subagent with `references/reviewer-brief.md`. Give
   it the scope and the diff, not this conversation, so it reads the code as
   written rather than as intended. Judge each finding: accept and fix it, or
   reject it with a one-line reason. Findings are advice to verify, not orders.
   After fixing, re-verify and review again, at most two rounds. Blocking
   findings still open after that go in the PR as open.
   Done when: a round is clean, or two rounds have run.

5. **Close.** Commit with a Conventional Commit message, then use the `pr`
   skill. Then use the `reflect` skill.
   Done when: the PR is open.

## Output

Reply with the PR link and two to four sentences: the problem, what changed,
the proof, and anything still open.

## Guardrails

- Leave unknown changes in the worktree alone.
- No merge, deploy, or production change without explicit approval.
- Keep credentials, tokens, and patient data out of tests, logs, and PRs.
