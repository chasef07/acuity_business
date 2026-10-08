"""Tests for pull_calls.py. Synthetic calls only; no patient data."""

import json
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import pull_calls


def call(**overrides):
    base = {
        "id": "00000000-0000-0000-0000-000000000001",
        "started_at": "2026-10-07T14:00:00+00:00",
        "ended_at": "2026-10-07T14:02:30+00:00",
        "status": "COMPLETED",
        "appointment_outcome": "BOOKING",
        "service_subject": "abita-s2s",
        "version_agent": "0.13.3",
        "version_prompts": None,
        "closeout": {"closeReason": "caller_hangup", "evaluation": {"status": "complete", "results": {}}},
        "work_tasks": [],
        "transcript": {"chat_history": {"items": []}},
    }
    base.update(overrides)
    return base


def items(*entries):
    return {"chat_history": {"items": list(entries)}}


class DayWindow(unittest.TestCase):
    def test_new_york_midnight_in_utc(self):
        start, end = pull_calls.day_window("2026-10-07", 1)
        self.assertEqual(start, datetime(2026, 10, 7, 4, tzinfo=timezone.utc))
        self.assertEqual(end, datetime(2026, 10, 8, 4, tzinfo=timezone.utc))

    def test_window_spanning_dst_end_is_25_hours(self):
        start, end = pull_calls.day_window("2026-11-01", 1)
        self.assertEqual(start, datetime(2026, 11, 1, 4, tzinfo=timezone.utc))
        self.assertEqual(end, datetime(2026, 11, 2, 5, tzinfo=timezone.utc))


class DatabaseUrl(unittest.TestCase):
    def test_reads_user_password_and_database_ignoring_socket_host(self):
        env = pull_calls.connection_env(
            "postgres://acuity_portal:p%40ss@localhost/acuity_product?host=/cloudsql/x", 54329
        )
        self.assertEqual(env["PGUSER"], "acuity_portal")
        self.assertEqual(env["PGPASSWORD"], "p@ss")
        self.assertEqual(env["PGDATABASE"], "acuity_product")
        self.assertEqual(env["PGHOST"], "127.0.0.1")
        self.assertEqual(env["PGPORT"], "54329")
        self.assertIn("default_transaction_read_only=on", env["PGOPTIONS"])


class PromptTag(unittest.TestCase):
    def test_prefers_prompt_version(self):
        self.assertEqual(pull_calls.prompt_tag(call(version_prompts="0.12.0")), "prompts-v0.12.0")

    def test_falls_back_to_agent_release(self):
        self.assertEqual(pull_calls.prompt_tag(call()), "v0.13.3")

    def test_unknown_without_versions(self):
        self.assertIsNone(pull_calls.prompt_tag(call(version_agent=None)))


class Render(unittest.TestCase):
    def test_transcript_keeps_full_tool_results_and_offsets(self):
        long_output = "slot " * 500
        text = pull_calls.render_call(
            7,
            call(
                transcript=items(
                    {"type": "message", "role": "user", "content": ["hi"], "created_at": 1000.0},
                    {"type": "function_call", "name": "list_available_appointments", "call_id": "c1",
                     "arguments": "{\"day\": \"mon\"}", "created_at": 1003.5},
                    {"type": "function_call_output", "call_id": "c1", "output": long_output,
                     "is_error": True, "created_at": 1065.0},
                    {"type": "message", "role": "assistant", "content": [{"text": "Monday works"}],
                     "interrupted": True, "created_at": "1970-01-01T00:18:10+00:00"},
                )
            ),
        )
        self.assertIn("# Call 007", text)
        self.assertIn("[00:00] caller: hi", text)
        self.assertIn('[00:03] tool call list_available_appointments({"day": "mon"})', text)
        self.assertIn("[01:05] tool result list_available_appointments ERROR:", text)
        self.assertIn(long_output, text)
        self.assertIn("[01:30] agent (interrupted): Monday works", text)


class Stats(unittest.TestCase):
    def test_counts_silence_transfers_tools_and_tasks(self):
        calls = [
            call(transcript=items({"type": "message", "role": "user", "content": [""]})),
            call(
                transcript=items(
                    {"type": "message", "role": "user", "content": ["leave a message"]},
                    {"type": "function_call", "name": "search_office_knowledge", "call_id": "a"},
                    {"type": "function_call_output", "call_id": "a", "output": "Office hours are 9 to 5."},
                    {"type": "function_call", "name": "save_staff_task", "call_id": "b1"},
                    {"type": "function_call_output", "call_id": "b1", "output": "saved: Draft saved.\nDraft ID: d1"},
                    {"type": "function_call", "name": "save_staff_task", "call_id": "b2"},
                    {"type": "function_call_output", "call_id": "b2", "output": "saved: Draft saved.\nDraft ID: d1"},
                    {"type": "function_call", "name": "save_staff_task", "call_id": "b3"},
                    {"type": "function_call_output", "call_id": "b3", "output": "saved: Draft saved.\nDraft ID: d2"},
                    {"type": "function_call", "name": "save_staff_task", "call_id": "b4",
                     "arguments": "{\"draft_id\": \"d2\", \"cancel\": true}"},
                    {"type": "function_call_output", "call_id": "b4", "output": "cancelled: Request cancelled."},
                    {"type": "function_call", "name": "transfer_call", "call_id": "c"},
                    {"type": "function_call_output", "call_id": "c", "output": "failed: No line.", "is_error": True},
                    {"type": "function_call", "name": "transfer_call", "call_id": "e"},
                    {"type": "function_call_output", "call_id": "e", "output": "blocked: Transfers are off."},
                )
            ),
        ]
        stats = pull_calls.compute_stats(calls)
        self.assertEqual(stats["calls"], 2)
        self.assertEqual(stats["no_caller_speech"], [{"call": 1, "caller_items": 1}])
        self.assertEqual(stats["tool_results"]["transfer_call"], {"error": 1, "blocked": 1})
        self.assertEqual(stats["tool_results"]["save_staff_task"], {"saved": 3, "cancelled": 1})
        self.assertEqual(stats["tool_results"]["search_office_knowledge"], {"other": 1})
        self.assertEqual(stats["transfers"]["calls"], [{"call": 2, "tools_before": ["search_office_knowledge"] + ["save_staff_task"] * 4}])
        self.assertEqual(stats["staff_tasks"]["mismatches"], [{"call": 2, "drafts": 1, "work_tasks": 0}])


class Batches(unittest.TestCase):
    def test_balances_by_size(self):
        batches = pull_calls.balance({"a": 9, "b": 5, "c": 3, "d": 1}, 2)
        self.assertEqual(sorted(sorted(b) for b in batches), [["a"], ["b", "c", "d"]])


class OutputDirectory(unittest.TestCase):
    def test_refuses_a_directory_inside_a_git_repository(self):
        with tempfile.TemporaryDirectory() as root:
            subprocess.run(["git", "init", "-q", root], check=True)
            with self.assertRaises(SystemExit):
                pull_calls.prepare_out(Path(root) / "calls")

    def test_refuses_a_non_empty_directory(self):
        with tempfile.TemporaryDirectory() as root:
            (Path(root) / "old.json").write_text(json.dumps({}))
            with self.assertRaises(SystemExit):
                pull_calls.prepare_out(Path(root))


if __name__ == "__main__":
    unittest.main()
