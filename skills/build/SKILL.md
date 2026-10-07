---
name: build
description: "Build a feature or fix in one repository: prove the problem is real, trace the current code, agree the plan, build test-first, then loop with a fresh reviewer for bugs, simplicity, and scope. Use when asked to build, implement, or fix something."
---

# Build

Prove the change is worth making, make it as small as possible, and get fresh
eyes on it before anyone else does.

## Use when

- Building a feature or fixing a bug in one repository.

## Not for

- Work across several repositories or workstreams. Use the `orchestrator`
  skill.

## Steps

1. **Frame.** Before editing anything, write:
   - **Real?** The evidence the problem exists: a failing test, log, call,
     report, or reproduction. For a new feature, the request is the evidence.
     A bug with no evidence is marked `UNPROVEN`.
   - **Now:** what the code does today, traced through the actual files and
     functions.
   - **Proposed:** the smallest change that fixes it, and what it leaves alone.
   - **Done when:** the proof that will close it.

   Show the frame, then continue without waiting.
   Done when: all four parts are written with evidence.

2. **Build.** Work on a branch, test first: write a test that fails for the
   reason in the frame, then the least code that makes it pass, one slice at a
   time. Use subagents only for independent changes in different files. Note
   problems outside the frame; do not fix them. Leave cleanup to review.
   Done when: the new test passes, and fails without the change.

3. **Verify.** Run the repository's checks and the proof from the frame.
   "It compiles" is not proof.
   Done when: checks pass and the proof is captured.

4. **Review.** Start a fresh subagent with `references/reviewer-brief.md`. Give
   it the frame and the diff, not this conversation, so it reads the code as
   written rather than as intended. Judge each finding: accept and fix it, or
   reject it with a one-line reason. Findings are advice to verify, not orders.
   After fixing, re-verify and review again, at most two rounds. Blocking
   findings still open after that go in the PR as open.
   Done when: a round is clean, or two rounds have run.

5. **Close.** Commit with a Conventional Commit message and open a draft PR
   with the frame, proof, and review summary. Put `UNPROVEN` and open findings
   at the top. Then use the `reflect` skill.
   Done when: the draft PR shows before-and-after proof.

## Output

```text
Frame:        real? / now / proposed / done when
Proof:        <test red -> green, command output, call replay>
Review:       round 1: 2 blocking fixed, 1 nit rejected (<reason>); round 2: clean
Open:         <blocking findings left after two rounds, or none>
Footprint:    +142 / -38 across 4 files
PR:           <link> (draft)
Out of scope: <noted, not fixed>
```

## Guardrails

- Leave unknown changes in the worktree alone.
- No merge, deploy, or production change without explicit approval.
- Keep credentials, tokens, and patient data out of tests, logs, and PRs.
