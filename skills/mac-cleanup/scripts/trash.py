#!/usr/bin/env python3
"""Move paths into one dated folder in the Trash, keeping their paths.

Usage: trash.py [--dest DIR] [--root DIR] PATH...

Relative paths resolve against ROOT (default: the home folder) and keep that
relative path under DEST. Absolute paths outside ROOT keep their full path
under DEST. DEST defaults to ~/.Trash/cleanup-YYYY-MM-DD.

Prints one line per path: moved, missing, or failed with the reason. Exits 1
if any move failed. Uses rename only, so a move never copies data or deletes
anything; a path on another volume fails instead of being copied.
"""

import argparse
import os
import sys
from datetime import date
from pathlib import Path


def destination(path, root, dest):
    source = Path(path) if os.path.isabs(path) else root / path
    try:
        relative = source.relative_to(root)
    except ValueError:
        relative = source.relative_to(source.anchor)
    return source, dest / relative


def move(path, root, dest):
    source, target = destination(path, root, dest)
    if not source.exists() and not source.is_symlink():
        return f"missing {path}", True
    if target.exists():
        return f"failed {path}: {target} already exists", False
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        os.rename(source, target)
    except OSError as error:
        return f"failed {path}: {error.strerror}", False
    return f"moved {path}", True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", type=Path,
                        default=Path.home() / ".Trash" / f"cleanup-{date.today()}")
    parser.add_argument("--root", type=Path, default=Path.home())
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()

    ok = True
    for path in args.paths:
        line, moved = move(path, args.root, args.dest)
        print(line)
        ok = ok and moved
    print(f"trash folder: {args.dest}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
