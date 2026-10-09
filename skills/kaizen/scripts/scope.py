#!/usr/bin/env python3
"""Export each repo's origin default branch and pick this week's audit scope.

Usage: scope.py --out DIR [--days 7] [--hot 15] [--week N]

For each repo, fetches origin, exports the default branch with `git archive`
into DIR/<repo> (the local checkout and its branch are never touched), and
writes DIR/scope.json:

  week                ISO week number used to pick the rotating area
  repos.<name>.root   exported tree to review
  repos.<name>.sha    commit the export came from
  repos.<name>.hot    most-changed source files in the last N days
  repos.<name>.area   this week's rotating module and its source files

DIR must be empty and outside any git repository.
"""

import argparse
import fnmatch
import io
import json
import subprocess
import sys
import tarfile
from collections import Counter
from datetime import date
from pathlib import Path

HOME = Path.home()
REPOS = {
    "acuity_product": {
        "path": HOME / "acuity_product",
        "areas": ["backend/internal/*", "web/src/*"],
        "skip_areas": ["backend/internal/api", "backend/internal/migrations", "backend/internal/testdb",
                       "backend/internal/testaccess", "web/src/types", "web/src/mdx-components.tsx"],
    },
    "abita_s2s": {"path": HOME / "abita_s2s", "areas": ["src/abita_s2s/*"], "skip_areas": ["src/abita_s2s/__init__.py"]},
    "amd_middleware": {"path": HOME / "amd_middleware", "areas": ["internal/*"], "skip_areas": []},
}
SOURCE = (".go", ".py", ".ts", ".tsx", ".js", ".mjs")
GENERATED = ("*.gen.go", "*.gen.ts", "*_gen.go", "*/generated/*", "*.pb.go", "*/node_modules/*")


def git(repo, *args):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} in {repo}: {p.stderr.decode().strip()}")
    return p.stdout


def is_source(path):
    return path.endswith(SOURCE) and not any(fnmatch.fnmatch(path, g) for g in GENERATED)


def default_branch(repo):
    ref = git(repo, "symbolic-ref", "--short", "refs/remotes/origin/HEAD").decode().strip()
    return ref or "origin/main"


def hot_files(repo, branch, days, limit):
    log = git(repo, "log", branch, f"--since={days} days ago", "--name-only", "--format=").decode()
    counts = Counter(p for p in log.splitlines() if p and is_source(p))
    tracked = set(git(repo, "ls-tree", "-r", "--name-only", branch).decode().splitlines())
    return [{"file": f, "commits": n} for f, n in counts.most_common() if f in tracked][:limit]


def areas(repo, branch, patterns, skip):
    tracked = git(repo, "ls-tree", "-r", "--name-only", branch).decode().splitlines()
    found = set()
    for pattern in patterns:
        depth = pattern.count("/") + 1
        for path in tracked:
            parts = path.split("/")
            candidate = "/".join(parts[:depth])
            if is_source(path) and fnmatch.fnmatch(candidate, pattern) and candidate not in skip:
                found.add(candidate)
    names = sorted(found)
    return names, tracked


def area_for_week(names, tracked, week):
    if not names:
        raise RuntimeError("no rotating areas found")
    name = names[week % len(names)]
    files = [p for p in tracked if (p == name or p.startswith(name + "/")) and is_source(p)]
    return {"name": name, "index": week % len(names), "of": len(names), "files": files}


def export(repo, branch, dest):
    archive = git(repo, "archive", "--format=tar", branch)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(dest, filter="data")


def prepare_out(out):
    out = out.resolve()
    probe = out if out.exists() else out.parent
    inside = subprocess.run(["git", "-C", str(probe), "rev-parse", "--is-inside-work-tree"], capture_output=True, text=True)
    if inside.stdout.strip() == "true":
        sys.exit(f"refusing {out}: it is inside a git repository")
    if out.exists() and any(out.iterdir()):
        sys.exit(f"refusing {out}: directory is not empty")
    out.mkdir(parents=True, exist_ok=True)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--hot", type=int, default=15)
    parser.add_argument("--week", type=int, default=date.today().isocalendar().week)
    args = parser.parse_args()

    out = prepare_out(args.out)
    scope = {"week": args.week, "days": args.days, "repos": {}}
    for name, cfg in REPOS.items():
        repo = cfg["path"]
        git(repo, "fetch", "--quiet", "origin")
        branch = default_branch(repo)
        names, tracked = areas(repo, branch, cfg["areas"], set(cfg["skip_areas"]))
        export(repo, branch, out / name)
        scope["repos"][name] = {
            "root": str(out / name),
            "checkout": str(repo),
            "branch": branch,
            "sha": git(repo, "rev-parse", branch).decode().strip(),
            "hot": hot_files(repo, branch, args.days, args.hot),
            "area": area_for_week(names, tracked, args.week),
        }
        print(f"{name}: {len(scope['repos'][name]['hot'])} hot files, area {scope['repos'][name]['area']['name']}", file=sys.stderr)
    (out / "scope.json").write_text(json.dumps(scope, indent=2))
    print(out / "scope.json")


if __name__ == "__main__":
    main()
