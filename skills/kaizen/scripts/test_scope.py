"""Tests for scope.py against a throwaway git repository."""

import subprocess
import tempfile
import unittest
from pathlib import Path

import scope


def make_repo(root, files):
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    for path, text in files.items():
        p = root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    subprocess.run(["git", "-C", str(root), "add", "."], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init"], check=True)


class Source(unittest.TestCase):
    def test_generated_and_non_code_are_excluded(self):
        self.assertTrue(scope.is_source("internal/work/server.go"))
        self.assertFalse(scope.is_source("backend/internal/api/openapi.gen.go"))
        self.assertFalse(scope.is_source("web/src/content/page.mdx"))


class Areas(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        make_repo(self.repo, {
            "internal/alpha/a.go": "package alpha",
            "internal/beta/b.go": "package beta",
            "internal/docs/readme.md": "no code",
            "internal/skip/s.go": "package skip",
            "main.go": "package main",
        })

    def tearDown(self):
        self.tmp.cleanup()

    def test_only_areas_with_source_and_not_skipped(self):
        names, _ = scope.areas(self.repo, "main", ["internal/*"], {"internal/skip"})
        self.assertEqual(names, ["internal/alpha", "internal/beta"])

    def test_week_rotates_through_areas(self):
        names, tracked = scope.areas(self.repo, "main", ["internal/*"], set())
        picked = [scope.area_for_week(names, tracked, week)["name"] for week in range(4)]
        self.assertEqual(picked, ["internal/alpha", "internal/beta", "internal/skip", "internal/alpha"])
        self.assertEqual(scope.area_for_week(names, tracked, 0)["files"], ["internal/alpha/a.go"])

    def test_hot_files_count_commits(self):
        hot = scope.hot_files(self.repo, "main", 7, 10)
        self.assertIn({"file": "main.go", "commits": 1}, hot)
        self.assertFalse(any(h["file"].endswith(".md") for h in hot))


if __name__ == "__main__":
    unittest.main()
