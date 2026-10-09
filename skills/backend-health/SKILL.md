---
name: backend-health
description: "Check production backend health in acuity-health-prod against Google SRE's four golden signals: latency, traffic, errors, and saturation. Use when asked whether the backend is healthy, after a release, or when calls or the portal seem broken."
---

# Backend Health

Report whether the production backend is healthy right now, measured by the
four golden signals, with evidence for each one.

## Use when

- Asked "is the backend healthy?" or "check backend health".
- Right after a production release.
- Staff report that the portal or calls are slow or failing.

## Scope

Project `acuity-health-prod`, region `us-east1`. Services: `acuity-portal-api`,
`acuity-provider-ingress`, `acuity-realtime`, and the `acuity-worker` worker
pool. `acuity-web` and `abita-middleware` (us-east4) are outside this skill;
mention their errors only as context.

## Steps

1. **Pull.** Run:

   ```bash
   ~/acuity_business/skills/backend-health/scripts/pull_health.py [--minutes 60] > <scratchpad>/health.json
   ```

   It probes each service and pulls the last N minutes (default 60) from Cloud
   Monitoring and Cloud Logging, read-only, in about 20 seconds. Every source
   it could not read is listed in `unknown` with the reason. If gcloud auth
   fails, ask the user to run `gcloud auth login`.
   Done when: the script exits 0. Each `unknown` entry is reported as `UNKNOWN`
   for the signal it feeds; a log read that hit its row limit means rerun with
   fewer minutes.

2. **Deploy** (`deploy`). Every `live` and `health_ready` is 200, every runtime
   is `ready`, and every `commit` matches `latest_release.sha`. If `since` falls
   inside the window, say so: errors right after a deploy may be startup.

3. **Latency** (`latency`). The checked provisional limit is p99 above 1s on
   `service_seconds`, `critical_routes`, and `other_routes`. `call_path` has no
   checked limit; report it, and flag only a clear jump.

4. **Traffic** (`traffic`). Compare `requests` with `requests_24h_earlier` by
   service and status class, and report `webhooks`. A service or route with no
   traffic where yesterday had some is `UNKNOWN`, not healthy.

5. **Errors** (`errors`, `availability`). `availability.ratio` must meet the
   0.999 SLO. For each `server_errors` group, its `nearest_app_line` is the
   likely cause; with none, the cause is `UNKNOWN`. Report `app_errors`, which
   includes the worker, the same way.
   Done when: every error group has a cause, or is marked `UNKNOWN`.

6. **Saturation** (`saturation`). Findings: any `quarantined_depth` above zero,
   a queue `oldest_*` age that is high at `latest`, a `latest`
   `saturation_ratio` of 1, any `no_available_instance`, or `peak_instances`
   near the runtime's `max_instances`. A `peak` that has gone back to zero at
   `latest` is transient.

7. **Verdict.** Mark the backend healthy only if all four signals pass. A burst
   that has stopped is reported as transient, with its time range. A burst
   that is still happening, or a backlog that is growing, means unhealthy.

8. **Post** the report to Slack `#product` (`C0C0KP8707R`). Keep it short. A
   healthy result with no suggested changes is a complete report.
   Done when: the message link is in the reply to the user.

## Output

```markdown
**Backend health: healthy | degraded | unhealthy** (<window>, release <version> / <sha>)

| Signal | Result | Evidence |
|---|---|---|
| Latency | pass/fail | p50/p99 per service; call-path p99 |
| Traffic | pass/fail/UNKNOWN | requests/hr vs yesterday; webhooks; SSE active |
| Errors | pass/fail | availability %; error groups |
| Saturation | pass/fail | pool ratio; queue depth/age; quarantine |

**Errors** (UTC; leave this section out when there are none)
- <service> <route> <status> ×<n>, <first>–<last>: <cause or UNKNOWN>; recurring/transient

**Suggested changes**
- <change>: <why, from the evidence above>
(or "None.")
```

## Guardrails

- Read-only. Never deploy, roll back, or change traffic or scaling from this
  skill. Hand any fix to `build`.
- Log fields are fixed metric labels. Never copy call IDs, phone numbers, or
  request bodies into the report.
- Say when a signal has no data. Don't call silence healthy.
