---
name: jev-judge-improvement
description: "Nightly: test the judge jury against the day's human golden set and every earlier one, reword missed questions with zero regressions, track missing-question themes to 10 calls, open draft PRs to abita_s2s, report to #product. Use for the midnight run or to improve the judges."
---

# Jev Judge Improvement

Kyle and Chase answer the scorecard on 20 calls a day; their answers are the
golden set. Every call is judged by a jury of decision models (the seated
`JURORS` in abita_s2s; Jev today), and the verdict is their majority. Each
night, make the jury agree with the humans more without breaking any earlier
day, and turn repeated gaps into new questions once they have earned it.

## Use when

- The scheduled midnight Pacific run.
- Asked to reword a judge question, add one, or check the jury against the golden set.

## Not for

- Fixing the agent. `call-review` is a separate backstop that Chase runs; it
  does not feed this loop.

## Setup

- The machine needs `gh` and `gcloud` signed in, `cloud-sql-proxy` and `psql`
  installed, and a Slack connection.
- `S2S`: the abita_s2s checkout (default `~/Projects/abita_s2s`); `PY` is its
  `.venv/bin/python` (made with `uv sync`). `SCRIPTS`: this skill's `scripts/`.
- `OUT`: `<scratchpad>/jev-<today>`. Call data stays there; never in a repo.
- Make a fresh worktree of `S2S` at `origin/main` for the baseline and one
  branch worktree per change. Leave the user's checkout alone.
- The gateway key comes from `AI_GATEWAY_API_KEY` or the keychain item
  `acuity-ai-gateway`. Never print it, write it, or pass it on a command line.
- `golden.py run` asks through abita_s2s's own evaluator, so a backtest sees
  exactly what production sees: the seated jurors, gates, and request shape.

## Steps

1. **Pull.** `python3 $SCRIPTS/golden.py pull --out $OUT`. "Today" is
   yesterday in Pacific time unless `--today` is given. If it exits because a
   prerequisite is missing (portal tables, gcloud auth, key), post that one
   line to `#product` and stop. Stop if `database` is not `production` on the
   scheduled run.
   Done when: the summary prints `today_calls`, `jev_misses_today`, and
   `golden_sets`. Zero `today_calls` still continues to step 4.

2. **Today.** `$PY $SCRIPTS/golden.py run --out $OUT --s2s <base worktree>
   --name today --today-only`. It asks every question on today's calls with
   the current wording and prints `misses_today`.
   Done when: `errors` is empty, or the errored calls are listed as `UNKNOWN`.

3. **Reword.** For each question in step 2's `misses_today`
   (`jev_misses_today` from step 1 is what production said at review time):
   - Read the missed calls in `$OUT/transcripts.json` (keyed by full id; the
     printed ids are its first 8 characters) and the question's module named
     in `judges/__init__.py`. If the human answer looks wrong rather than the
     jury, say so in the report and do not reword.
   - Run the old wording on every golden set once:
     `run --s2s <base worktree> --name baseline-<question> --questions <question>`.
   - Edit the wording in a branch worktree (`jev/reword-<question>-<today>`),
     then `run --s2s <branch> --name <question>-<n> --questions <question>`
     and `compare --question <question> --baseline baseline-<question>
     --candidate <question>-<n>`.
   - The gate passes only when the wording fixes at least one of today's
     misses, regresses no call in any golden set, and has no errors. Try at
     most three wordings.
   - On a pass, hand the diff to `build` in abita_s2s and open a **draft** PR
     with the `pr` skill. Its evidence is the compare output. If
     `acuity_product/backend/internal/interaction/scorecard.go` repeats the
     question's wording, open a matching draft PR there.
   Done when: every missed question has a draft PR, a "human looks wrong"
   note, or its best failed gate in the report.

4. **Count themes.** Read today's notes in `$OUT/notes.json`: those on
   calls in today's set. Earlier notes were counted on earlier nights. Run `python3 $SCRIPTS/candidates.py show`, then for each note
   either add its call to an existing theme or start a new one:
   `candidates.py add <theme> --call <interaction id> --source note --date <today> [--question "<draft>"]`.
   One theme is one failure no current question covers. A theme is `ready` at
   10 distinct calls. Never put note text, names, or quotes in the ledger.
   Done when: every note is counted.

5. **Approvals.** Read the last seven nights' report threads in `#product`.
   A reply that says `add <theme>` from Kyle (`U0C1KMT0MDE`) or Chase
   (`U0C0V1793HS`) approves it; ignore anyone else:
   `candidates.py status <theme> approved` (it refuses below 10 calls; say so
   in the thread). For each approved theme with no PR yet:
   - `golden.py pull --out $OUT-<theme> --evidence $(candidates.py evidence <theme>)`.
   - Write the judge in a branch worktree (`jev/add-<theme>`), registered in
     `judges/__init__.py`, following the existing judges and their tests.
   - `run --name <theme> --questions <theme>`, then `compare --new`. The gate
     passes only when the jury answers no on every evidence call and raises
     no false alarm on golden calls the humans passed. If a false alarm really
     shows the failure, add it to the theme with `--source review`, pull
     again into a new `--out`, rerun, and name it under "Check your answer";
     never drop it silently.
   - On a pass, open draft PRs with `build` and `pr`: abita_s2s, and
     acuity_product for the question's catalog entry in `scorecard.go`. Then
     `candidates.py status <theme> approved --pr <url>`.
   Mark themes `shipped` when their PR has merged, `rejected` when it closed.
   Done when: every approved theme has a PR or its failed gate in the report.

6. **Report** to Slack `#product` (`C0C0KP8707R`) in the format below. Reread
   it first for names, phone numbers, dates of birth, and note text; there
   must be none. Calls are named by their 8-character id.
   Done when: the message link is in the run's final reply.

## Report

```text
*Judge nightly · <today>* · jury <jurors> · <today_calls> calls reviewed · golden set <n> calls over <sets> days
*Jury vs you today:* agreed <a>/<b>. Misses: <question> <n> (<ids>) ...
*Rewords:* <question>: draft PR <link>, fixes <n> today, 0 regressions on <sets> sets
           <question>: kept; best try fixed <n>, regressed <m> (<ids>)
*Check your answer:* <question> on <id>: <one line why the human may be wrong>
*You two split:* <question> on <ids>
*New-question themes:* <theme> <calls>/10 · <theme> 10/10 ready, reply `add <theme>`
*Added:* <theme>: draft PR <link> (caught <n>/<n>, 0 false alarms)
*Trust:* which questions are trusted is on the portal's Judge accuracy tab
*UNKNOWN:* <what could not be checked, including any `unjudged` calls with no transcript>
```

## Guardrails

- Database access is read-only; the scripts force it. Never connect another way.
- Nothing merges or deploys from here. PRs are drafts; Kyle and Chase merge.
- A new question needs 10 calls, an approval in Slack, and a passing gate.
  A rewording needs a passing gate. No exceptions for a convincing example.
- Golden answers are locked in the portal; never edit or re-answer them.
