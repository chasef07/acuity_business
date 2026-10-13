#!/usr/bin/env python3
"""Audit the code folders in a directory before a cleanup, read-only.

Usage: audit_repos.py [ROOT]   (default: the home folder)

Prints one row per top-level folder, oldest last commit first:
  tier         re-clone | wip | only-copy
  size_mb      disk use
  last_commit  date of the newest commit, or "-"
  real         uncommitted changes that are real work
  junk         uncommitted changes that are only junk (.DS_Store, logs, agent folders)
  unpushed     commits on local branches that no remote has
  remote       origin, or "-"

Tiers:
  re-clone   git, has a remote, nothing unpushed, only junk uncommitted
  wip        git with real changes, unpushed commits, or no remote
  only-copy  not a git repo: this machine has the only copy

File modification times are not used: an earlier migration resets them.
"""

import subprocess
import sys
from pathlib import Path

SKIP = {"Applications", "Desktop", "Documents", "Downloads", "Library", "Movies",
        "Music", "Pictures", "Public"}
JUNK_DIRS = (".claude/", ".cursor/", ".playwright-mcp/", "__pycache__/")


def git(folder, *args):
    result = subprocess.run(["git", "-C", str(folder), *args],
                            capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def is_junk(path):
    name = path.rstrip("/").rsplit("/", 1)[-1]
    return (name == ".DS_Store" or path.endswith(".log")
            or any(path.startswith(d) or f"/{d}" in path for d in JUNK_DIRS))


def split_dirty(porcelain):
    """Split `git status --porcelain` output into (real, junk) path lists."""
    real, junk = [], []
    for line in porcelain.splitlines():
        path = line[3:].split(" -> ")[-1].strip('"')
        (junk if is_junk(path) else real).append(path)
    return real, junk


def tier(is_repo, remote, unpushed, real):
    if not is_repo:
        return "only-copy"
    if not remote or unpushed or real:
        return "wip"
    return "re-clone"


def audit(folder):
    size_kb = int(subprocess.run(["du", "-sk", str(folder)], capture_output=True,
                                 text=True).stdout.split()[0] or 0)
    toplevel = git(folder, "rev-parse", "--show-toplevel")
    is_repo = toplevel is not None and Path(toplevel).resolve() == folder.resolve()
    row = {"name": folder.name, "size_mb": size_kb // 1024, "last_commit": "-",
           "real": 0, "junk": 0, "unpushed": 0, "remote": "-"}
    if is_repo:
        real, junk = split_dirty(git(folder, "status", "--porcelain") or "")
        unpushed = git(folder, "log", "--branches", "--not", "--remotes", "--oneline") or ""
        row.update(last_commit=git(folder, "log", "-1", "--format=%cs") or "-",
                   real=len(real), junk=len(junk),
                   unpushed=len(unpushed.splitlines()),
                   remote=git(folder, "remote", "get-url", "origin") or "-")
    row["tier"] = tier(is_repo, row["remote"] != "-", row["unpushed"], row["real"])
    return row


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path.home())
    folders = [p for p in sorted(root.iterdir())
               if p.is_dir() and not p.is_symlink()
               and not p.name.startswith(".") and p.name not in SKIP]
    rows = sorted((audit(f) for f in folders), key=lambda r: r["last_commit"])
    columns = ["tier", "name", "size_mb", "last_commit", "real", "junk", "unpushed", "remote"]
    print("\t".join(columns))
    for row in rows:
        print("\t".join(str(row[c]) for c in columns))


if __name__ == "__main__":
    main()
