---
name: reflect
description: "Turn what happened in a task into lasting fixes: a check, a skill edit, or a one-line repo note, delivered as PRs. Use when build or orchestrator work closes, after the user corrects the agent, or when asked to reflect. Finding nothing is a valid result."
---

# Reflect

Make the next run better than this one. Prefer a check over a note: a note can
be ignored, a failing test cannot.

## Use when

- `build` or `orchestrator` work closes.
- The user corrected the agent, or a session went badly.

## Steps

1. **Gather signals.** From this task, list the user's corrections, the
   reviewer's findings, failed checks or tests, retries, `BLOCKED` or `FAILED`
   workers, `UNPROVEN` frames, and anything the agent had to work around.
   Done when: every signal is listed, or there are none.

2. **Keep lessons that will repeat.** Drop one-offs, weak evidence, and
   anything an existing check, skill, or note already covers. Most runs end here
   with "nothing to learn."
   Done when: each remaining lesson names the signal that proves it.

3. **Route each lesson** to the first destination that fits:
   1. **Check:** a test, lint rule, or hook in the product repository. Anything
      mechanical belongs here.
   2. **Skill:** an edit to a skill in `~/acuity_business/skills/`, such as a
      new rule in the `build` reviewer brief. Follow
      `~/acuity_business/docs/writing-skills.md`. Removing a stale rule counts.
   3. **Note:** one line in the product repository's `AGENTS.md`, for judgement
      calls a check cannot catch.

   Done when: every lesson has one destination.

4. **Deliver as PRs** written with the `pr` skill. Do not wait for approval;
   merging the PR is the approval.
   - Checks and notes: commit on the task's branch so they appear in its PR.
     With no task branch, open a draft PR in the product repository.
   - Skill edits: a new branch and draft PR in `acuity_business`, after
     `scripts/validate-skills` passes.

   Done when: every change is in a PR.

## Output

```text
Lessons:
- <lesson> (signal: <what proved it>) -> check | skill | note: <PR link>

or

Nothing to learn: <one-line reason>
```

## Guardrails

- One lesson, one small change. Never commit to `main`.
- Leave unknown changes in a worktree alone.
- Keep credentials, tokens, and patient data out of lessons.
