"""Tests for pull_health.py. Synthetic log entries only."""

import unittest

import pull_health


def request(at, url, status, latency="0.1s", service="acuity-portal-api"):
    return {
        "timestamp": at,
        "resource": {"labels": {"service_name": service}},
        "httpRequest": {"requestUrl": url, "status": status, "latency": latency},
    }


def app(at, msg, cause=None, severity="WARNING", service="acuity-portal-api"):
    return {
        "timestamp": at,
        "severity": severity,
        "resource": {"labels": {"service_name": service}},
        "jsonPayload": {"msg": msg, "cause": cause},
    }


class Route(unittest.TestCase):
    def test_ids_are_collapsed(self):
        url = "https://x.run.app/v1/calling/calls/af8455d8-8646-45d5-bc85-f0f50ba610f4/retry"
        self.assertEqual(pull_health.route(url), "/v1/calling/calls/{id}/retry")


class Labels(unittest.TestCase):
    def test_route_slashes_do_not_split_labels(self):
        ts = {"metric": {"labels": {"route": "/v1/access", "outcome": "available"}}}
        key = pull_health.labels(ts, ("metric.labels.route", "metric.labels.outcome"))
        self.assertEqual(key.split(" | "), ["/v1/access", "available"])

    def test_no_group_is_all(self):
        self.assertEqual(pull_health.labels({}, ()), "all")


class GroupErrors(unittest.TestCase):
    def test_groups_by_route_and_attaches_nearest_cause(self):
        requests = [
            request("2026-10-08T18:39:19Z", "https://x/v1/agent/knowledge/search", 503, "3.01s"),
            request("2026-10-08T18:39:01Z", "https://x/v1/agent/knowledge/search", 503, "3.00s"),
        ]
        lines = [
            app("2026-10-08T18:39:02Z", "office_knowledge_search_failed", "deadline_exceeded"),
            app("2026-10-08T18:39:01Z", "unrelated", service="acuity-realtime"),
            app("2026-10-08T18:30:00Z", "too_early"),
        ]
        [g] = pull_health.group_errors(requests, lines)
        self.assertEqual((g["route"], g["status"], g["count"]), ("/v1/agent/knowledge/search", 503, 2))
        self.assertEqual((g["first"], g["last"]), ("2026-10-08T18:39:01Z", "2026-10-08T18:39:19Z"))
        self.assertEqual(g["max_seconds"], 3.01)
        self.assertEqual(g["nearest_app_line"]["msg"], "office_knowledge_search_failed")
        self.assertEqual(g["nearest_app_line"]["cause"], "deadline_exceeded")

    def test_no_app_line_in_range_is_none(self):
        [g] = pull_health.group_errors([request("2026-10-08T17:36:45Z", "https://x/v1/tasks", 503)], [])
        self.assertIsNone(g["nearest_app_line"])


class AppErrors(unittest.TestCase):
    def test_counts_by_message_and_skips_request_lines(self):
        entries = [
            app("2026-10-08T14:00:00Z", "boom", severity="ERROR", service="acuity-worker"),
            app("2026-10-08T14:05:00Z", "boom", severity="ERROR", service="acuity-worker"),
            request("2026-10-08T14:01:00Z", "https://x/v1/tasks", 500),
        ]
        entries[0]["resource"]["labels"] = {"worker_pool_name": "acuity-worker"}
        entries[1]["resource"]["labels"] = {"worker_pool_name": "acuity-worker"}
        [g] = pull_health.count_app_errors(entries)
        self.assertEqual((g["runtime"], g["msg"], g["count"]), ("acuity-worker", "boom", 2))
        self.assertEqual((g["first"], g["last"]), ("2026-10-08T14:00:00Z", "2026-10-08T14:05:00Z"))


class Gauges(unittest.TestCase):
    def test_latest_and_peak_per_metric_and_role(self):
        def line(at, depth):
            return {"timestamp": at, "jsonPayload": {
                "metric": "acuity_call_center_receipt_queue", "runtime_role": "worker",
                "revision": "r1", "depth": depth, "quarantined_depth": 0}}
        out = pull_health.summarize_gauges([line("2026-10-08T14:02:00Z", 0), line("2026-10-08T14:01:00Z", 5)])
        g = out["acuity_call_center_receipt_queue/worker"]
        self.assertEqual(g["latest"], {"depth": 0, "quarantined_depth": 0})
        self.assertEqual(g["peak"], {"depth": 5, "quarantined_depth": 0})
        self.assertEqual(g["latest_at"], "2026-10-08T14:02:00Z")


class SourceFailures(unittest.TestCase):
    def test_failed_read_is_named_unknown(self):
        src = pull_health.Source()

        def broken():
            raise RuntimeError("permission denied")

        self.assertIsNone(src.read("request count", broken))
        self.assertEqual(src.unknown, [{"source": "request count", "reason": "permission denied"}])


if __name__ == "__main__":
    unittest.main()
