# Worker Brief

Fill in and send. Give the worker only the context it needs.

```text
Goal:       <the outcome this work serves, one sentence>
Task:       <the one workstream>
Where:      <repository path or ops area>
Limits:     <allowed actions and hard stops>
Context:    <Linear issue, files, evidence, links>
Done when:  <the proof that closes it>

Follow the repository's AGENTS.md and relevant skills.
Stay in scope. Do not start other workers.
Leave unknown changes in the worktree alone.
Report BLOCKED when a limit, missing access, or missing evidence stops you.

Return exactly:
Verdict:   DONE | BLOCKED | FAILED
Proof:     <test output, diff summary, link, or record; pointers, not prose>
Changed:   <files, PRs, drafts, records>
Blocker:   <what stopped you, or none>
Decision:  <what Chase must decide, or none>
Next:      <recommended next step>
```

Default limits: read, edit locally, open a PR. No merge, deploy, outside
send or post, production change, spending, or data deletion.

On a retry after `FAILED`, add one line before `Return exactly:`:

```text
Previous attempt: <what failed and what it learned>
```
