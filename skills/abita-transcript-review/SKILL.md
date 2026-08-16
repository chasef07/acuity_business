---
name: abita-transcript-review
description: "Review Abita AgentCall evidence from the acuity_site portal database for AcuityLoops voice-agent reliability work. Use for transcript audits, loop runs, high-signal call investigation, worker handoffs, and transcript-backed PR evidence across abita_agent, abita_middleware, and acuity_site."
---

# Abita Transcript Review

Find real call failures from production evidence. Route the fix to the owning boundary. Stay read-only unless the loop, task, or worker boundary explicitly grants implementation.

## Sources

- Loop root: `/Users/chasefagen/Projects/acuityhealthloops`
- Portal repo and database env: `/Users/chasefagen/acuity_site`
- Fix owners:
  - `abita_agent`: prompt, voice runtime, state, tool definitions, tool guards
  - `abita_middleware`: AMD/API truth, availability, booking, cancellation, insurance contracts
  - `acuity_site`: ingestion, normalization, review jobs, portal analytics
  - `Chase`: office policy, clinical policy, privacy, money, customer decision

Re-check current code before present-tense claims:

- `prisma/schema.prisma`
- `lib/call-types.ts`
- `lib/call-normalization.ts`
- `lib/admin-analytics.ts`
- `lib/portal-overview.ts`

## AcuityLoops Contract

- Read the relevant goal, goal state, loop, loop state, and run template before acting when this is a loop run.
- Save completed loop runs under `runs/voice-agent-reliability/` when the caller asks for a run.
- Update loop state with durable learning.
- Update goal state only when learning is broader than one run.
- Do not invent work when evidence is weak.

## Modes

### Triage

- Aggregate first.
- Use structured fields and `data.toolExecutions`.
- Always audit unsupported outcome claims for booked, cancelled, confirmed, rescheduled, held, updated, routed, or insurance-handled claims.
- Do not inspect raw transcripts unless a high-signal candidate needs review.
- Classify signals as `Autonomous`, `Needs Chase`, `Monitor`, `Data gap`, or `No action`.
- Reuse existing work for the same issue class.

### Review

- Inspect only selected calls.
- Compare caller request, agent promise, loaded state, tool call/result, final flags, and backend-confirmed state when available.
- Treat any agent claim of a completed appointment or insurance outcome without matching proof as a hallucination candidate.
- Use short paraphrases, turn numbers, tool names, and final-state proof.
- Do not dump transcript text.

### Handoff

- One worker equals one repo/task.
- Include sanitized call IDs, exact evidence, suspected owner boundary, expected validation, and the smallest safe fix.
- Grant PR creation only when the current task explicitly allows it.

## Hard Rules

- Start with `git -C /Users/chasefagen/acuity_site status -sb`.
- Load `.env.local` without echoing values.
- Run read-only SQL unless implementation is explicitly allowed.
- Never print secrets, tokens, `DATABASE_URL`, phone numbers, DOBs, member IDs, patient names, private customer context, or raw transcripts.
- Weak evidence means `No action`, `Monitor`, or `Data gap`.
- A recovered tool error can be `Monitor`, not automatically a bug.
- Missing `reviewStatus`, `reviewResult`, or `needsReview` is not a blocker.
- If database access is missing, stop with the exact missing piece.

Safe env-key check:

```bash
cd /Users/chasefagen/acuity_site
perl -ne 'print "$1\n" if /^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=/' .env.local | sort
```

## Database Access

Use the portal database from `/Users/chasefagen/acuity_site`.

- Load `/Users/chasefagen/acuity_site/.env.local` without printing values.
- Use `DATABASE_URL`.
- Prisma model: `AgentCall`.
- Physical table: `agent_call`.
- Query read-only by default.

Important columns:

- `id`
- `callId`
- `practiceId`
- `startedAt`
- `status`
- `transferred`
- `bookedAppointment`
- `confirmedAppointment`
- `cancelledAppointment`
- `toolCalls`
- `toolErrors`
- `outcomeSummary`
- `data`

Useful JSON paths:

- `data.turns`
- `data.toolExecutions`
- `data.sessionReport.chat_history.items`
- `data.callState`
- `data.appointmentActions`

Minimal query pattern:

```js
import dotenv from "dotenv";
import pg from "pg";

dotenv.config({ path: "/Users/chasefagen/acuity_site/.env.local" });

const { Pool } = pg;
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

const result = await pool.query(`
  select id, "callId", "startedAt", status, "toolErrors", "outcomeSummary", data
  from agent_call
  where "startedAt" >= now() - interval '24 hours'
  order by "startedAt" desc
  limit 50
`);

await pool.end();
```

## Signals

Prioritize correctness before polish:

1. Unsupported outcome claim: the agent said an appointment was booked, cancelled, confirmed, rescheduled, held, updated, routed, or insurance was handled, but no matching successful tool execution, appointment action, final flag, or backend-confirmed state supports it.
2. Agent promised success but tool/backend did not confirm it.
3. Final `AgentCall` flags contradict tool results.
4. Tool errors on booking, reschedule, cancel, transfer, insurance, or identity.
5. Repeated tool loops after a clear request.
6. Transfer after avoidable tool/runtime failure.
7. Failed review with tool or final-state evidence.
8. Language, latency, silence, or interruption tied to concrete events.

Handle legacy aliases only when present, such as `book_appt`, `reschedule_appt`, or `cancel_appt`.

## Checks

- Outcome claim: every claimed booking, cancellation, confirmation, reschedule, hold, routing update, insurance update, or insurance check must have matching tool/result, appointment action, final flag, or backend-confirmed state.
- Booking: exact slot offered, caller confirmed, tool succeeded, final state reflects it.
- Reschedule: old appointment identified, new slot confirmed, no accidental new booking, final state reflects it.
- Cancel: appointment identity and explicit cancel confirmation are clear.
- Confirm: patient and appointment target are clear before confirmation.
- Insurance: medical vs routine vision lane is right; ambiguity does not loop.
- Transfer: valid for emergency, caller insistence, unsupported request, or office policy; suspicious as avoidable fallback.
- Language: detected language, tool/runtime language, and TTS response language stay coherent.
- Latency: isolate STT, EOU, LLM, tool, TTS, and provider/runtime gaps when traces exist.

## Classify

- `Autonomous`: clear bug or deterministic improvement with focused validation path.
- `Needs Chase`: product, office policy, clinical, privacy, money, credential, or customer decision.
- `Monitor`: real signal but not worth a change yet.
- `Data gap`: evidence or source of truth is missing.
- `No action`: behavior correct or evidence too weak.

## Output

Keep it compact.

```text
Window: <range>
Calls scanned: <n>
Flagged: <n>
Autonomous: <n>
Needs Chase: <n>
Monitor/Data gap: <n>

Unsupported Outcome Claims:
- Status: <none found|candidate|confirmed>
- Call: <sanitized call id, or none>
- Claimed outcome: <short paraphrase, no transcript dump>
- Backing proof: <matching proof or missing proof>
- Owner: <abita_agent|abita_middleware|acuity_site|Chase|none>
- Action: <fix|worker|monitor|ask Chase|no action>

Finding:
- Call: <sanitized call id>
- Symptom: <one line>
- Evidence: <tool/final-state proof, no PHI>
- Owner: <abita_agent|abita_middleware|acuity_site|Chase>
- Confidence: <high|medium|low>
- Action: <fix|worker|monitor|ask Chase|no action>
```

## Worker Handoff

```text
Title: <owner>: <short issue>
Repo: <absolute repo path>
Task: <exact issue and sanitized call evidence>
Boundary: <inspect only|local edit|draft PR>; no direct main push, merge, release, destructive git, secrets, raw transcripts, or PHI.
Expected proof: <focused test/check and review evidence>

Use $abita-transcript-review for the evidence pass.
Respect dirty worktrees.
Implement the smallest deterministic fix at the right boundary.
Use Codex review when a review closeout is needed.
Open a draft PR only when the boundary grants PR creation and checks pass.
```

## PR Evidence

For transcript-backed fixes, include:

- `Issue`: production symptom and aggregate count.
- `Evidence`: sanitized call IDs plus short tool/final-state proof.
- `Why it failed`: prompt, runtime state, tool contract, middleware/API, ingestion, or policy boundary.
- `Fix`: what changed and why that boundary owns it.
- `Benefit`: expected production improvement.
- `Validation`: focused checks and review status when run.

Never include raw transcripts, phone numbers, DOBs, member IDs, patient names, credentials, private URLs, or office-sensitive context in public PR bodies.
