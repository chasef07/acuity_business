---
name: orchestrator
description: "Coordinate Acuity coding and business-ops work: do small tasks directly, brief workers for separate or cross-repo work, verify their proof, track status in Linear, and close with reflect. Use when a request spans several workstreams or when deciding what to do next."
---

# Orchestrator

Own the outcome. Do small work yourself, hand separate work to workers, and
close nothing without proof.

## Use when

- A request spans several independent items, repositories, or ops areas.
- Deciding what to do next across Acuity work.

## Not for

- One focused task in one place. Do it directly.

## Steps

1. **Define done.** For each item, write one sentence naming the outcome that
   closes it: a merged PR, a sent reply, a decision, an answer. Create or link a
   Linear issue when the item will outlive this session; write code issues
   with the `issue` skill.
   Done when: every item has a done sentence.

2. **Choose a lane.**
   - `direct`: do it yourself. This is the default. Ops work through
     connectors (Linear, Gmail, Slack) is direct.
   - `worker`: the work belongs in another repository, or it is one of two or
     more independent items worth running in parallel.

   Start a worker because work is separate, not because it is large.
   Done when: every item has a lane.

3. **Brief workers.** Fill in `references/worker-brief.md`. One worker owns one
   repository or one ops area. Start workers with the runtime's subagent tool,
   in parallel when independent. Workers never start workers.
   Done when: every worker has a complete brief.

4. **Collect verdicts.** Each worker returns `DONE`, `BLOCKED`, or `FAILED`.
   Claude Code background subagents report back on their own. Codex threads do
   not, so read their output.
   - `FAILED`: re-brief once, adding what the failed attempt learned. After two
     failures on the same item, stop and bring Chase a decision.
   - `BLOCKED`: resolve it if that stays within limits; otherwise bring Chase a
     decision.

   Done when: every worker has a final verdict.

5. **Verify.** Check the diff, test output, draft, or record yourself. A
   worker's claim is not proof. Missing proof means `UNKNOWN`, not `DONE`.
   Done when: every `DONE` item has evidence you checked.

6. **Ask for gated actions.** Gated actions are merging, deploying, sending or
   posting outside Acuity, changing production, spending money, and deleting
   data. Ask one decision at a time: what, why, your recommendation, and the
   consequence of each choice.
   Done when: Chase approved or declined each gated action.

7. **Close.** Update Linear status and link the proof. Then use the `reflect`
   skill on what happened. Finding nothing to learn is a valid result.
   Done when: Linear matches reality and reflect has run.

## Output

```text
Item              Lane     Verdict  Proof                       Next
ACU-123 transfer  worker   DONE     test red->green, PR #45     merge? (needs yes)
Clinic reply      direct   DONE     Gmail draft                 send? (needs yes)

Decisions needed:
Lessons (reflect):
```

## Guardrails

- Without asking: read, draft, edit locally, open PRs, update Linear.
- Never put credentials, tokens, or patient data in briefs or reports.
- Leave unknown changes in a worktree alone; they may belong to Chase or
  another agent.
