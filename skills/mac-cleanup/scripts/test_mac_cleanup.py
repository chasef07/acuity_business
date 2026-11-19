"""Tests for audit_repos.py and trash.py. Temporary folders only."""

import subprocess
import tempfile
import unittest
from pathlib import Path

import audit_repos
import trash


def run(*args, cwd):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True)


def make_repo(path):
    path.mkdir()
    run("git", "init", "-q", "-b", "main", cwd=path)
    (path / "a.txt").write_text("a")
    run("git", "add", ".", cwd=path)
    run("git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init", cwd=path)


class SplitDirty(unittest.TestCase):
    def test_junk_is_separated_from_real_work(self):
        porcelain = "\n".join([
            " M src/agent.ts",
            "?? .DS_Store",
            "?? app/.DS_Store",
            "?? .claude/",
            "?? .playwright-mcp/console.log",
            "R  old.ts -> new.ts",
        ])
        real, junk = audit_repos.split_dirty(porcelain)
        self.assertEqual(real, ["src/agent.ts", "new.ts"])
        self.assertEqual(len(junk), 4)


class Tier(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(audit_repos.tier(False, False, 0, 0), "only-copy")
        self.assertEqual(audit_repos.tier(True, False, 0, 0), "wip")
        self.assertEqual(audit_repos.tier(True, True, 2, 0), "wip")
        self.assertEqual(audit_repos.tier(True, True, 0, 1), "wip")
        self.assertEqual(audit_repos.tier(True, True, 0, 0), "re-clone")


class Audit(unittest.TestCase):
    def test_pushed_repo_is_reclone_and_plain_folder_is_only_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root / "work")
            run("git", "init", "-q", "--bare", str(root / "remote.git"), cwd=root)
            run("git", "remote", "add", "origin", str(root / "remote.git"), cwd=root / "work")
            run("git", "push", "-q", "origin", "main", cwd=root / "work")
            (root / "work" / ".DS_Store").write_text("")
            (root / "notes").mkdir()

            self.assertEqual(audit_repos.audit(root / "work")["tier"], "re-clone")
            self.assertEqual(audit_repos.audit(root / "notes")["tier"], "only-copy")

    def test_unpushed_commit_is_wip(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_repo(Path(tmp) / "work")
            row = audit_repos.audit(Path(tmp) / "work")
            self.assertEqual((row["tier"], row["unpushed"]), ("wip", 1))


class Trash(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "home"
        self.dest = Path(self.tmp.name) / "trash"
        (self.root / "Library" / "Caches" / "go-build").mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_relative_path_keeps_its_path(self):
        line, ok = trash.move("Library/Caches/go-build", self.root, self.dest)
        self.assertTrue(ok, line)
        self.assertTrue((self.dest / "Library" / "Caches" / "go-build").is_dir())
        self.assertFalse((self.root / "Library" / "Caches" / "go-build").exists())

    def test_missing_path_is_reported_not_failed(self):
        self.assertEqual(trash.move("nope", self.root, self.dest), ("missing nope", True))

    def test_existing_target_is_never_overwritten(self):
        (self.dest / "Library" / "Caches" / "go-build").mkdir(parents=True)
        line, ok = trash.move("Library/Caches/go-build", self.root, self.dest)
        self.assertFalse(ok)
        self.assertIn("already exists", line)
        self.assertTrue((self.root / "Library" / "Caches" / "go-build").is_dir())

    def test_absolute_path_outside_root_keeps_full_path(self):
        outside = Path(self.tmp.name) / "opt" / "data"
        outside.mkdir(parents=True)
        _, target = trash.destination(str(outside), self.root, self.dest)
        self.assertEqual(target, self.dest / outside.relative_to(outside.anchor))


if __name__ == "__main__":
    unittest.main()
