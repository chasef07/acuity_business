---
name: mac-cleanup
description: "Audit and clean a Mac: stale code folders, caches, unused apps, orphaned background jobs, loose secrets, and dead shell config. Use when asked to clean up the laptop, free disk space, or prepare for a migration."
---

# Mac Cleanup

Free space and remove stale work from a Mac without losing anything the user
still needs: survey, show evidence, let the user pick, move to the Trash.

## Use when / Not for

- Use when asked to clean the laptop, free disk space, or prepare a migration.
- Not for cleaning inside one repo (branches, dead code); use `kaizen`.

## Steps

1. **Survey.** Run `df -h /`, then `du -sh` on `~/*`, `~/.*`, `~/Library/*`,
   `~/Library/Caches/*`, and `~/Library/Application Support/*`.
   Done when: you know free space and the 20 largest folders.

2. **Audit code folders.** Run `scripts/audit_repos.py` (default root: home).
   It sorts each folder into `re-clone`, `wip`, or `only-copy` by git state,
   not file dates. For `wip` folders, read the real changes.
   Done when: every code folder has a tier.

3. **Audit the rest.**
   - Caches that rebuild: go-build and `go/pkg/mod`, `Library/pnpm/store`,
     `.npm/_cacache`, `.bun/install/cache`, `.cache/uv`, Playwright, Homebrew,
     app updaters, `com.apple.wallpaper/aerials/videos`.
   - Apps: `/Applications`, with last use from each app's data folder mtime
     (Spotlight's last-used date is often empty). Leftover data from
     uninstalled apps.
   - Background: `~/Library/LaunchAgents`, `/Library/Launch*`, login items,
     `crontab -l`. Flag jobs whose paths no longer exist.
   - Config: `~/.zshrc` lines for removed tools, old `nvm` versions, Homebrew
     leaves with no users (`brew uses --installed`), dot folders for tools no
     longer installed.
   - Secrets and data that must not migrate: production DB dumps, call
     recordings, loose `.pem` keys, API keys written into `~/.zshrc`.
   Done when: each item has a size and a recommendation.

4. **Present tiers and ask.** Group items as rebuildable caches, `re-clone`
   repos, and decisions for the user (`wip`, `only-copy`, VMs, local
   databases, apps, old Downloads).
   Done when: the user has picked what goes.

5. **Check what depends on each pick.**
   - Symlinks into it: `find ~/.claude ~/.codex -maxdepth 2 -type l -lname '*<folder>*'`.
     The skills folders link into `~/acuity_business` (2026-10-12: removing it
     broke 8 skills).
   - Running processes: `pgrep -fl <name>`. A parent PID of 1 means orphaned;
     confirm its session is gone before stopping it.
   - Launch agents that reference the path; Homebrew data in `/opt/homebrew/var`.
   Done when: every dependency is stopped, kept, or approved by the user.

6. **Move.** Run `scripts/trash.py <paths>`. It renames into
   `~/.Trash/cleanup-<date>/` with original paths, so anything can be put back.
   For mixed folders, pass only the cache part (pnpm `store`, bun
   `install/cache`). Unload a launch agent with
   `launchctl bootout gui/$(id -u)/<label>` before moving its plist. For a git
   worktree, move it, then run `git -C <main repo> worktree prune`.
   Done when: the script exits 0.

7. **Verify.** Open a fresh shell (`zsh -ic 'node -v; bun -v'`) and recheck
   `df -h /`.
   Done when: the shell loads without errors.

## Output

```markdown
**Mac cleanup:** <free before> → <free after emptying Trash>

| Moved | Size |
|---|---|
| <group> | <GB> |

Kept: <active repos and apps>
Your steps: empty the Trash; <sudo commands, login items, keys to rotate>
```

## Guardrails

- Move, never delete. Emptying the Trash, `sudo`, login items, key rotation,
  and saving keys to a password manager are the user's steps.
- `only-copy` and `wip` folders move only after the user names them.
- In zsh, a glob with no match aborts the command; use
  `bash -c 'shopt -s nullglob; ...'` for glob sweeps.
