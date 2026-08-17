---
name: backend-health
description: "Assess a Google Cloud backend using the four golden signals: latency, traffic, errors, and saturation. Use for production health checks, incident diagnosis, or recurring backend reviews that must grade each signal and explain anything that is not green."
---

# Backend Health

Perform a read-only health check. Use current evidence, the last 24 hours, and a
7-day comparison window.

## Guardrails

- Do not edit code, deploy, scale, restart, replay work, or mutate production.
- Pass `--project` explicitly. Do not change the user's active `gcloud` project.
- Sanitize logs and output. Do not expose credentials, tokens, PHI, or customer data.
- Treat missing evidence as `UNKNOWN`, never `GREEN`.

## Use the Google Cloud CLI

Confirm the CLI, account, token, and project before making health claims:

```sh
command -v gcloud
gcloud auth list --filter=status:ACTIVE --format='value(account)'
gcloud auth print-access-token >/dev/null
gcloud config get project
gcloud projects describe PROJECT_ID --format=json
```

If authentication is missing or expired, stop and report `BLOCKED:
AUTHENTICATION`. Tell the user to run `gcloud auth login`; never request their
password or token.

Discover and inspect Cloud Run services with:

```sh
gcloud run services list --platform=managed --project=PROJECT_ID --format=json
gcloud run services describe SERVICE --region=REGION --project=PROJECT_ID --format=json
```

Query Cloud Monitoring through its read-only time-series API using the access
token from `gcloud auth print-access-token`. Never print or save the token. Use
`gcloud logging read` with explicit project, time, service, revision, and result
limits when diagnosis requires logs.

## Check the Four Golden Signals

1. **Latency** — Measure successful and failed request latency separately. Report
   p50, p95, and p99 when available. Start with
   `run.googleapis.com/request_latencies`.
2. **Traffic** — Measure request volume and rate, including unexpected loss or
   spikes. Start with `run.googleapis.com/request_count`. Traffic is context;
   more traffic is not automatically bad.
3. **Errors** — Measure 5xx count and rate, SLO burn, failed operations, and new
   error signatures. Do not classify expected 4xx responses as backend failures
   without evidence.
4. **Saturation** — Measure CPU, memory, concurrency, pending requests, instance
   pressure, database connections, and queue pressure when available. Start with
   `run.googleapis.com/container/cpu/utilizations`,
   `run.googleapis.com/container/memory/utilizations`,
   `run.googleapis.com/container/max_request_concurrencies`,
   `run.googleapis.com/pending_queue/pending_requests`, and
   `run.googleapis.com/scaling/recommended_instances`.

Use repository runtime contracts, SLOs, and alert thresholds as the targets. If
no target exists, grade the signal `UNKNOWN` and state what must be defined.

## Grade Health

- `GREEN` — Within target, sufficient data exists, and no relevant incident is active.
- `YELLOW` — Near target, materially worse than baseline, or recently recovered.
- `RED` — Target violated, actionable incident active, or customer behavior failing.
- `UNKNOWN` — Data, permissions, expected behavior, or a target is missing.

Overall health is the worst signal: `RED`, then `UNKNOWN`, then `YELLOW`, then
`GREEN`. Call the backend green only when all four signals are green.

## Diagnose Anything Not Green

For every `YELLOW`, `RED`, or `UNKNOWN` signal:

1. Identify the service, revision, time window, and observable failure.
2. Compare the failing window with the 7-day baseline and recent deployments.
3. Inspect bounded, sanitized logs and dependency or resource metrics.
4. Name the likely owner: application, database, dependency, capacity, traffic,
   or observability.
5. Separate proven cause from hypothesis and recommend one next action.

Weak evidence means no-change is valid. Do not claim a root cause without proof.

## Report

```text
Overall: GREEN | YELLOW | RED | UNKNOWN

Signal       Status    Evidence    Diagnosis
Latency      ...       ...         ...
Traffic      ...       ...         ...
Errors       ...       ...         ...
Saturation   ...       ...         ...

Active problems:
Recovered problems:
Missing evidence:
Recommended next action:
```

Keep a green report brief. For every non-green signal, include the exact evidence
window and the commands or queries used.
