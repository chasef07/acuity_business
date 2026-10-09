#!/usr/bin/env python3
"""Pull production backend health as the four golden signals, read-only.

Usage: pull_health.py [--minutes N]

Prints one JSON document to stdout:
  window       UTC bounds of the last N minutes (default 60)
  deploy       probes, image commit, ready-since, and latest release per runtime
  latency      p50/p99 per service, per critical route, and on the call path
  traffic      requests by service and status class, now and 24h earlier
  errors       5xx groups with the nearest app log line, and app ERROR lines
  saturation   latest and peak database pool, queue, and instance values
  unknown      every source that could not be read, with the reason

Numbers come from Cloud Monitoring (Cloud Run metrics and the checked
log-based metrics). Logs are read only for errors and for gauge lines, which
are low volume. Nothing is written to Google Cloud.
"""

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

PROJECT = "acuity-health-prod"
REGION = "us-east1"
REPO = "chasef07/acuity_product"
IMAGE = f"{REGION}-docker.pkg.dev/{PROJECT}/acuity-product/backend"
SERVICES = ["acuity-portal-api", "acuity-provider-ingress", "acuity-realtime"]
WORKER = "acuity-worker"
MONITORING = f"https://monitoring.googleapis.com/v3/projects/{PROJECT}/timeSeries"
USER_METRIC = "logging.googleapis.com/user/"
GAUGES = [
    "acuity_call_center_database_pool",
    "acuity_call_center_receipt_queue",
    "acuity_call_center_recording_queue",
    "acuity_call_center_terminal_cleanup",
    "acuity_call_center_sse_stream",
]
# Gauge fields that say how full something is. Everything else on the line is a label.
GAUGE_SKIP = {"metric", "metric_contract", "runtime_role", "revision", "state", "level", "msg", "time"}
UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
CAUSE_SECONDS = 5


class Source:
    """Collects reads that failed so the report can name them as UNKNOWN."""

    def __init__(self):
        self.unknown = []

    def read(self, name, fn, *args):
        try:
            return fn(*args)
        except Exception as e:  # each failure is reported, never swallowed
            detail = e.read().decode(errors="replace") if isinstance(e, urllib.error.HTTPError) else ""
            self.unknown.append({"source": name, "reason": f"{e} {detail}".strip()[:300]})
            return None


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd[:4])}...: {p.stderr.strip()[:300]}")
    return p.stdout


def gcloud_json(*args):
    return json.loads(run(["gcloud", *args, f"--project={PROJECT}", "--format=json"]) or "null")


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def route(url):
    path = urllib.parse.urlsplit(url or "").path or url or ""
    return UUID.sub("{id}", path)


def seconds(latency):
    return float(latency.rstrip("s")) if latency else None


# ---------- deploy ----------

def probe(url):
    started = time.monotonic()
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            status = r.status
    except urllib.error.HTTPError as e:
        status = e.code
    except Exception as e:
        return {"status": None, "error": str(e)[:200]}
    return {"status": status, "seconds": round(time.monotonic() - started, 3)}


def ready_since(conditions):
    for c in conditions or []:
        if c.get("type") == "Ready":
            return {"ready": c.get("status") == "True", "since": c.get("lastTransitionTime")}
    return {"ready": False, "since": None}


def image_commit(image):
    digest = image.split("@", 1)[1] if "@" in image else None
    if not digest:
        raise RuntimeError(f"image is not pinned by digest: {image}")
    rows = gcloud_json("artifacts", "docker", "images", "list", IMAGE, "--include-tags", f"--filter=version={digest}")
    tags = [t for row in rows or [] for t in (row.get("tags") or [])]
    shas = [t for t in tags if re.fullmatch(r"[0-9a-f]{40}", t)]
    if not shas:
        raise RuntimeError(f"no commit tag on {digest}")
    return shas[0]


def latest_release():
    tag = run(["gh", "release", "view", "--repo", REPO, "--json", "tagName", "--jq", ".tagName"]).strip()
    sha = run(["gh", "api", f"repos/{REPO}/commits/{tag}", "--jq", ".sha"]).strip()
    return {"tag": tag, "sha": sha}


def deploy(src):
    runtimes = {}
    for name in SERVICES:
        svc = src.read(f"describe {name}", gcloud_json, "run", "services", "describe", name, f"--region={REGION}")
        if not svc:
            continue
        url = svc["status"]["url"]
        image = svc["spec"]["template"]["spec"]["containers"][0]["image"]
        runtimes[name] = {
            **ready_since(svc["status"].get("conditions")),
            "live": probe(f"{url}/health/live"),
            "health_ready": probe(f"{url}/health/ready"),
            "commit": src.read(f"commit {name}", image_commit, image),
            "max_instances": svc["spec"]["template"]["metadata"].get("annotations", {}).get(
                "autoscaling.knative.dev/maxScale"
            ),
        }
    pool = src.read(f"describe {WORKER}", gcloud_json, "beta", "run", "worker-pools", "describe", WORKER, f"--region={REGION}")
    if pool:
        image = pool["spec"]["template"]["spec"]["containers"][0]["image"]
        runtimes[WORKER] = {**ready_since(pool["status"].get("conditions")), "commit": src.read(f"commit {WORKER}", image_commit, image)}
    return {"runtimes": runtimes, "latest_release": src.read("latest release", latest_release)}


# ---------- Cloud Monitoring ----------

def token():
    return run(["gcloud", "auth", "print-access-token"]).strip()


def series(auth, metric_filter, start, end, aligner, reducer=None, group=(), period=None):
    period = period or int((end - start).total_seconds())
    params = [
        ("filter", metric_filter),
        ("interval.startTime", iso(start)),
        ("interval.endTime", iso(end)),
        ("aggregation.alignmentPeriod", f"{period}s"),
        ("aggregation.perSeriesAligner", aligner),
    ]
    if reducer:
        params.append(("aggregation.crossSeriesReducer", reducer))
        params += [("aggregation.groupByFields", g) for g in group]
    out, page = [], None
    while True:
        query = params + ([("pageToken", page)] if page else [])
        req = urllib.request.Request(f"{MONITORING}?{urllib.parse.urlencode(query)}", headers={"Authorization": f"Bearer {auth}"})
        with urllib.request.urlopen(req, timeout=30) as r:
            body = json.load(r)
        out += body.get("timeSeries", [])
        page = body.get("nextPageToken")
        if not page:
            return out


def labels(ts, group):
    found = {**ts.get("resource", {}).get("labels", {}), **ts.get("metric", {}).get("labels", {})}
    return " | ".join(found.get(g.rsplit(".", 1)[-1], "") for g in group) or "all"


def point(ts):
    v = ts["points"][0]["value"]
    for key in ("int64Value", "doubleValue"):
        if key in v:
            return float(v[key])
    return None


def by_label(rows, group, digits=3):
    return {labels(ts, group): round(point(ts), digits) for ts in rows if point(ts) is not None}


def summed(auth, metric_filter, start, end, group):
    return by_label(series(auth, metric_filter, start, end, "ALIGN_DELTA", "REDUCE_SUM", group), group, 0)


def percentiles(auth, metric_filter, start, end, group, scale=1.0):
    out = {}
    for name, reducer in (("p50", "REDUCE_PERCENTILE_50"), ("p99", "REDUCE_PERCENTILE_99")):
        for key, value in by_label(series(auth, metric_filter, start, end, "ALIGN_DELTA", reducer, group), group, 6).items():
            out.setdefault(key, {})[name] = round(value * scale, 3)
    return out


def user(metric):
    return f'metric.type="{USER_METRIC}{metric}"'


def run_metric(metric):
    names = ", ".join(f'"{s}"' for s in SERVICES)
    return (
        f'metric.type="run.googleapis.com/{metric}" AND resource.type="cloud_run_revision" '
        f'AND resource.labels.location="{REGION}" AND resource.labels.service_name=one_of({names})'
    )


def latency(src, auth, start, end):
    svc = ("resource.labels.service_name",)
    rt = ("metric.labels.route",)
    # Cloud Run reports request latency in milliseconds. Realtime requests are SSE
    # streams, so their latency is stream lifetime; /v1/events in other_routes is
    # the time to establish a stream.
    service = src.read("request latency", percentiles, auth, run_metric("request_latencies"), start, end, svc, 0.001)
    if service:
        service.pop("acuity-realtime", None)
    return {
        "service_seconds": service,
        "critical_routes": src.read("availability latency", percentiles, auth, user("acuity_backend_availability_seconds"), start, end, rt),
        "other_routes": src.read("route latency", percentiles, auth, user("acuity_backend_route_availability_seconds"), start, end, rt),
        "call_path": {
            "webhook_ack": src.read("webhook latency", percentiles, auth, user("acuity_call_center_webhook_acknowledgement_seconds"), start, end, ()),
            "provider_command": src.read("command latency", percentiles, auth, user("acuity_call_center_provider_command_duration_seconds"), start, end, ()),
            "answer_to_bridge": src.read("bridge latency", percentiles, auth, user("acuity_call_center_answer_to_bridge_seconds"), start, end, ()),
        },
    }


def traffic(src, auth, start, end):
    group = ("resource.labels.service_name", "metric.labels.response_code_class")
    day = timedelta(days=1)
    return {
        "requests": src.read("request count", summed, auth, run_metric("request_count"), start, end, group),
        "requests_24h_earlier": src.read("request count 24h", summed, auth, run_metric("request_count"), start - day, end - day, group),
        "webhooks": src.read("webhook count", summed, auth, user("acuity_call_center_webhook_acknowledgement_count"), start, end, ("metric.labels.outcome",)),
    }


def availability(src, auth, start, end):
    counts = src.read(
        "availability count", summed, auth, user("acuity_backend_availability_count"), start, end,
        ("metric.labels.route", "metric.labels.outcome", "metric.labels.failure_stage"),
    )
    if counts is None:
        return None
    total = sum(counts.values())
    available = sum(v for k, v in counts.items() if k.split(" | ")[1] == "available")
    return {"ratio": round(available / total, 5) if total else None, "slo": 0.999, "counts": counts}


def peak_instances(src, auth, start, end):
    # Sum each minute across revisions and states, then keep the busiest minute.
    def read():
        group = ("resource.labels.service_name",)
        rows = series(auth, run_metric("container/instance_count"), start, end, "ALIGN_MAX", "REDUCE_SUM", group, 60)
        return {labels(ts, group): max(float(p["value"]["int64Value"]) for p in ts["points"]) for ts in rows}
    return src.read("instance count", read)


# ---------- logs ----------

def logs(log_filter, start, end, limit):
    entries = gcloud_json(
        "logging", "read", f'{log_filter} AND timestamp>="{iso(start)}" AND timestamp<"{iso(end)}"', f"--limit={limit}"
    ) or []
    if len(entries) >= limit:
        raise RuntimeError(f"hit the {limit}-entry limit; shorten --minutes")
    return entries


def runtime_filter():
    names = " OR ".join(f'"{s}"' for s in SERVICES)
    return (
        f'((resource.type="cloud_run_revision" AND resource.labels.service_name=({names})) OR '
        f'(resource.type="cloud_run_worker_pool" AND resource.labels.worker_pool_name="{WORKER}"))'
    )


def runtime_of(entry):
    r = entry.get("resource", {}).get("labels", {})
    return r.get("service_name") or r.get("worker_pool_name") or "unknown"


def app_line(entry):
    p = entry.get("jsonPayload") or {}
    msg = p.get("msg") or p.get("message") or entry.get("textPayload") or ""
    return {"msg": str(msg)[:160], "cause": p.get("cause"), "level": level(entry)}


def group_errors(requests, app_lines):
    """Group 5xx requests by runtime, route, and status, each with its nearest app line."""
    groups = {}
    for e in requests:
        hr = e.get("httpRequest", {})
        key = (runtime_of(e), route(hr.get("requestUrl")), hr.get("status"))
        g = groups.setdefault(key, {"runtime": key[0], "route": key[1], "status": key[2], "count": 0, "times": [], "seconds": []})
        g["count"] += 1
        g["times"].append(e["timestamp"])
        if seconds(hr.get("latency")) is not None:
            g["seconds"].append(seconds(hr.get("latency")))
    out = []
    for g in groups.values():
        times = sorted(g.pop("times"))
        lat = g.pop("seconds")
        g.update(first=times[0], last=times[-1], max_seconds=round(max(lat), 3) if lat else None)
        g["nearest_app_line"] = nearest(g["runtime"], times[0], app_lines)
        out.append(g)
    return sorted(out, key=lambda g: -g["count"])


def nearest(runtime, at, app_lines):
    t = datetime.fromisoformat(at.replace("Z", "+00:00"))
    best = None
    for e in app_lines:
        if runtime_of(e) != runtime:
            continue
        gap = abs((datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00")) - t).total_seconds())
        if gap <= CAUSE_SECONDS and (best is None or gap < best[0]):
            best = (gap, e)
    return app_line(best[1]) if best else None


def count_app_errors(entries):
    groups = {}
    for e in entries:
        if e.get("httpRequest"):
            continue  # request log lines are covered by the 5xx groups
        line = app_line(e)
        key = (runtime_of(e), line["msg"], line["cause"])
        g = groups.setdefault(key, {"runtime": key[0], **line, "count": 0, "first": e["timestamp"], "last": e["timestamp"]})
        g["count"] += 1
        g["first"], g["last"] = min(g["first"], e["timestamp"]), max(g["last"], e["timestamp"])
    return sorted(groups.values(), key=lambda g: -g["count"])


def errors(src, start, end):
    base = runtime_filter()
    failed = src.read("5xx requests", logs, f"{base} AND httpRequest.status>=500", start, end, 2000)
    app = src.read(
        "app warnings", logs,
        # The backend writes its level into the payload and leaves severity unset.
        f'{base} AND (severity>=WARNING OR jsonPayload.level=("WARN" OR "ERROR")) AND -httpRequest:* '
        f'AND -jsonPayload.msg="call_center_metric"', start, end, 2000,
    )
    return {
        "server_errors": group_errors(failed or [], app or []),
        "app_errors": count_app_errors([e for e in app or [] if level(e) == "ERROR"]),
    }


def level(entry):
    if entry.get("severity") in ("ERROR", "CRITICAL", "ALERT", "EMERGENCY"):
        return "ERROR"
    return (entry.get("jsonPayload") or {}).get("level") or entry.get("severity")


def summarize_gauges(entries):
    """Latest and peak of each numeric gauge field, per metric and runtime role."""
    out = {}
    for e in sorted(entries, key=lambda e: e["timestamp"]):
        p = e.get("jsonPayload") or {}
        key = f'{p.get("metric")}/{p.get("runtime_role")}'
        g = out.setdefault(key, {"latest_at": None, "latest": {}, "peak": {}})
        g["latest_at"] = e["timestamp"]
        for field, value in p.items():
            if field in GAUGE_SKIP or not isinstance(value, (int, float)):
                continue
            g["latest"][field] = value
            g["peak"][field] = max(g["peak"].get(field, value), value)
    return out


def saturation(src, auth, start, end):
    names = " OR ".join(f'"{m}"' for m in GAUGES)
    lines = src.read("gauge lines", logs, f'jsonPayload.msg="call_center_metric" AND jsonPayload.metric=({names})', start, end, 20000)
    return {
        "gauges": summarize_gauges(lines) if lines is not None else None,
        "peak_instances": peak_instances(src, auth, start, end),
        "no_available_instance": src.read(
            "no instance errors", lambda: len(logs(f'{runtime_filter()} AND textPayload:"no available instance"', start, end, 500))
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--minutes", type=int, default=60)
    args = parser.parse_args()

    end = datetime.now(timezone.utc).replace(microsecond=0)
    start = end - timedelta(minutes=args.minutes)
    src = Source()
    try:
        auth = token()
    except RuntimeError as e:
        sys.exit(f"gcloud auth failed; run `gcloud auth login`: {e}")

    print("deploy...", file=sys.stderr)
    report = {"window": {"start": iso(start), "end": iso(end)}, "deploy": deploy(src)}
    print("monitoring...", file=sys.stderr)
    report["latency"] = latency(src, auth, start, end)
    report["traffic"] = traffic(src, auth, start, end)
    report["availability"] = availability(src, auth, start, end)
    print("logs...", file=sys.stderr)
    report["errors"] = errors(src, start, end)
    report["saturation"] = saturation(src, auth, start, end)
    report["unknown"] = src.unknown
    json.dump(report, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
