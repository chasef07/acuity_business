---
name: orchestrator
description: "Turn goals, tasks, scheduled wakeups, and AcuityLoops work into bounded worker-thread execution. Use when deciding what should happen next, creating or monitoring worker threads, closing delegated work with proof, updating a task pipeline, or promoting verified proof into durable wiki knowledge."
---

# Orchestrator

Keep the root thread light. Convert intent into bounded work, send the work to the right place, then close it with proof.

## Primitive

```text
Goal -> Task -> Worker Thread -> Proof -> Close -> Wiki Candidate
```

Workers execute. The orchestrator routes, monitors, and closes.

## Loop

1. Define done.
   - What artifact, PR, decision, proof, or outcome closes this?

2. Choose the lane.
   - `manual`: Chase should do it.
   - `worker`: a Codex thread should do it.
   - `automation`: a standing loop should do it.
   - `decision`: Chase must choose before work proceeds.
   - `no action`: not useful now.

3. Scope the work.
   - One worker equals one repo, domain, artifact, or task.
   - Do not create workers for vague, weak, speculative, or duplicate work.

4. Set the boundary.
   - Use plain language: inspect only, draft only, local edit, draft PR, publish approved, no external send, no production mutation.

5. Deploy or route.
   - Reuse an active worker if it already owns the same workstream.
   - Create a visible worker thread only for bounded work.
   - Name threads `<domain>: <short task>`, for example `abita_agent: insurance clarification guard`.
   - If the saved Codex project is `/Users/chasefagen/Projects`, do not use Codex app `worktree` mode for that folder because it is not a Git repo. Point the worker at the real repo root, such as `/Users/chasefagen/abita_agent`, or create a manual worktree from that repo.

6. Monitor.
   - Workers do not automatically report back.
   - Read the worker output before claiming completion.
   - Intervene only when blocked, unsafe, stale, done, or drifting.

7. Close.
   - Record status, proof, thread link, files/PR/artifact, blocker, decision needed, and next step.
   - Update the relevant pipeline, loop state, goal state, or weekly plan only when the change is durable.

8. Promote learning.
   - Decide whether verified proof contains durable knowledge that future workers should reuse.
   - Treat no wiki change as valid for task-local, duplicated, transient, private, or weak evidence.
   - When learning passes the promotion gate, deploy one bounded wiki subagent with `$acuity-wiki`.
   - Pass the verified closeout, source proof, target wiki location, and write boundary.
   - Read and verify the wiki result before claiming the system learned.
   - The root owns this fan-out. Repository workers do not spawn the wiki subagent.

## Worker Prompt

```text
Goal: <goal this work serves>
Thread: <domain>: <short task>
Task: <one exact workstream>
Boundary: <allowed actions and hard stops>
Context: <only relevant files, evidence, links, or constraints>

Use relevant local instructions and skills first.
Do not spawn subworkers or manage other threads.
Stay in scope.
Respect dirty worktrees.
Run focused checks when changing files.
Stop if the boundary, missing evidence, or unsafe action blocks progress.

Return:
- status
- output/artifact
- proof
- files/links changed
- blocker
- decision needed
- recommended next step
```

## Wiki Subagent Prompt

```text
Task: Promote verified worker proof into durable Acuity wiki knowledge.
Skill: Use $acuity-wiki.
Proof: <verified closeout and source links or paths>
Wiki target: <repository or directory>
Boundary: Documentation only. No product, production, external-send, or policy mutation.

Prefer updating an existing owner over creating a new entry.
No wiki change is valid when the learning is weak, transient, duplicated, or private.
Do not spawn subworkers.

Return:
- status
- wiki file changed
- proof used
- promotion-gate decision
- what future workers should do differently
- blocker or decision needed
```

## Boundaries

Examples:

- `Inspect only; no edits.`
- `Draft only; do not send or publish.`
- `Edit locally and report proof; do not push.`
- `Open a draft PR if checks pass.`
- `Publish only this approved item.`
- `Do not spend money, merge, release, delete, send externally, or mutate production without explicit approval.`

## Closeout States

- `done`
- `created work`
- `needs decision`
- `blocked`
- `closed as noise`
- `failed`

No vague progress closeouts.

## Decision Brief

When Chase needs to decide, bring:

- decision needed
- evidence
- options
- recommendation
- consequence of each option
- next action after the decision

## Stop Conditions

Stop and ask when:

- done is too ambiguous to route
- the worker boundary would be crossed
- destructive or irreversible action is needed
- money, legal, privacy, credential, external-send, deploy, merge, release, or production mutation approval is needed
- evidence is weak and action would be speculative
