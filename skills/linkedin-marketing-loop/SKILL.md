---
name: linkedin-marketing-loop
description: "Run Acuity Health LinkedIn marketing from the local linkedin_ops ledger. Use for Acuity company-page posts, stronger post drafting, approval packets, autonomous publishing, metrics checks, comment triage, and growth-loop reports."
---

# LinkedIn Marketing Loop

Run Acuity LinkedIn as a ledger-backed growth loop. Make better posts, not more process.

## Sources

- Project: `/Users/chasefagen/Projects/linkedin_ops`
- Ledger: `/Users/chasefagen/Projects/linkedin_ops/data/linkedin_ops.sqlite`
- CLI: `/Users/chasefagen/Projects/linkedin_ops/scripts/linkedin_ops.py`
- Campaign: `/Users/chasefagen/Projects/linkedin_ops/config/campaigns/ophthalmology-ai-receptionist.json`
- Policy: `/Users/chasefagen/Projects/linkedin_ops/config/policy.json`

Never print access tokens, client secrets, raw private comments, credentials, or private customer context.

## Goal

Help Acuity get more customers by publishing useful, specific, founder-level posts for ophthalmology practice owners, administrators, office managers, and operators.

## Modes

- `triage`: check auth, drafts, approved posts, published posts, blockers, and metrics.
- `draft`: create or improve posts in the ledger.
- `approval packet`: show exact drafts and recommend approve, revise, publish, or hold.
- `autonomous publish`: publish one safe company-page post when policy allows.
- `metrics`: sync/report performance and useful learning.
- `comment triage`: classify comments; do not reply unless explicitly allowed.

## Commands

```bash
cd /Users/chasefagen/Projects/linkedin_ops
python3 scripts/linkedin_ops.py auth-status
python3 scripts/linkedin_ops.py seed-campaign config/campaigns/ophthalmology-ai-receptionist.json
python3 scripts/linkedin_ops.py sync-metrics --days 30
python3 scripts/linkedin_ops.py sync-comments
python3 scripts/linkedin_ops.py list-posts --status DRAFT
python3 scripts/linkedin_ops.py list-posts --status APPROVED
python3 scripts/linkedin_ops.py autopublish --campaign ophthalmology-ai-receptionist --yes
python3 scripts/linkedin_ops.py report --campaign ophthalmology-ai-receptionist
```

Approval and manual publish:

```bash
python3 scripts/linkedin_ops.py show-post --post-id <id>
python3 scripts/linkedin_ops.py approve --post-id <id> --notes "<approval>"
python3 scripts/linkedin_ops.py publish --post-id <id> --yes
```

## Posting Freedom

Have freedom to write sharper posts when grounded in true Acuity facts.

Good posts can be:

- practical
- opinionated
- founder-written
- contrarian
- operational
- customer-problem-first
- short or medium length
- story, lesson, teardown, checklist, or point-of-view

Avoid generic AI commentary. Do not write like a product brochure.

Prefer concrete angles:

- phone tag and dropped demand
- after-hours capture
- front-desk relief
- scheduling workflow
- EMR booking
- transfer visibility
- call summaries
- no-show or recall workflows
- two-way texting
- workflow automation inside medical practices
- what Acuity is learning from real calls

Approved proof may be used when it sharpens the post:

- Acuity is live in a six-location ophthalmology practice.
- The practice had been dropping about 200 calls a week.
- Acuity helps capture and book roughly 200 appointments a week.
- Optional commercial line: over `$100k` in weekly captured revenue.

Use proof anonymously unless Chase explicitly approves naming the practice.

## Guardrails

- Do not invent facts, metrics, customer names, clinical claims, or guaranteed outcomes.
- Do not name customers without explicit approval.
- Do not reply, comment, send DMs, upload media, run paid promotion, or make unusual claims unless the task explicitly allows it.
- Autonomous company-page publishing is allowed only through `autopublish --campaign ophthalmology-ai-receptionist --yes`.
- Publish at most one post per automation run.

## Classify

Post:

- `Draft ready`
- `Needs revision`
- `Approved`
- `Published`
- `Hold`

Engagement:

- `Sales follow-up`
- `Comment reply needed`
- `Useful signal`
- `Ignore`
- `Data gap`
- `API blocker`

## Worker Handoff

```text
Goal: Get more customers
Thread: linkedin_ops: <short lane>
Repo: /Users/chasefagen/Projects/linkedin_ops
Task: <triage|draft|approval packet|autonomous publish|metrics|comment triage|publish approved post>
Boundary: <what is allowed and forbidden>

Use $linkedin-marketing-loop.
Ledger first.
Respect policy.
Return status, output, proof, blocker, decision needed, and next step.
```

## Output

Report only meaningful changes:

- drafts created or improved
- posts needing approval
- posts published
- metrics signal changed
- comments needing follow-up
- auth/API blockers
- next recommended growth action
