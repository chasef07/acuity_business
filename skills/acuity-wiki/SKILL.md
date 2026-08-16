---
name: acuity-wiki
description: "Promote verified Acuity worker proof into concise durable wiki knowledge. Use after a worker closes with evidence and the orchestrator needs to create or update reusable product, architecture, operations, failure-mode, or decision guidance without copying transient run history into the wiki."
---

# Acuity Wiki

Turn verified work into knowledge that improves future work. A worker result is
an input, not automatically a wiki entry.

## Required input

Require:

- the verified worker closeout;
- links or paths to the supporting proof;
- the target wiki repository or directory;
- the allowed write boundary.

Stop if the proof cannot be checked or the wiki target is ambiguous.

## Promotion gate

Promote only knowledge that future workers should reuse:

- a verified invariant or source-of-truth boundary;
- an approved product or architecture decision;
- a repeatable operating procedure;
- a recurring failure mode with a proven cause and fix;
- a durable exception, constraint, or ownership rule.

Do not promote:

- raw run output, logs, transcripts, or status updates;
- one-off branch, PR, deployment, or incident state;
- speculation, weak evidence, or unresolved disagreement;
- duplicated guidance already owned elsewhere;
- secrets, credentials, PHI, private customer context, or private URLs.

No wiki change is a valid closeout.

## Workflow

1. Read the target repository's `AGENTS.md`, vision, wiki index, and the most
   relevant existing entry.
2. Verify the closeout against its proof and identify what is actually durable.
3. Search for an existing owner. Prefer updating one entry over creating a new
   file or compatibility note.
4. Write the smallest useful change. State the current rule first, then why it
   exists, its evidence, and meaningful exceptions.
5. Link to sanitized source proof and record when the claim was last verified.
6. Check links, remove duplicated prose, and ensure the entry tells a future
   worker what to do differently.

Create at most one new wiki entry from one proof packet unless the orchestrator
explicitly scopes more.

## Entry shape

Use only the sections the knowledge needs:

```markdown
# <Durable topic>

## Current rule
## Why
## Evidence
## Exceptions
## Related
```

## Return

Return:

- status: `created`, `updated`, `no change`, or `needs decision`;
- wiki file changed;
- proof used;
- why the knowledge passed or failed the promotion gate;
- what future workers should now do differently;
- blocker or decision needed.

Do not spawn workers, change product behavior, mark the originating task done,
or rewrite vision or policy without explicit approval. The root orchestrator
verifies the wiki result and owns final closeout.
