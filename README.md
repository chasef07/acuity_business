# Acuity Business

The shared operating layer for Acuity Health agents: global working rules and a
small, curated set of skills used from Codex and Claude Code.

## Layout

- `AGENTS.md` — hard rules for every agent in every repository.
- `skills/` — reusable workflows. Each one earns its place.
- `docs/writing-skills.md` — how to write and change a skill.
- `scripts/validate-skills` — checks skill front matter and size limits.
- `scripts/link-skills` — links rules and skills into both agent runtimes.
- `hooks/` — local guardrails.

## Setup

```bash
git config core.hooksPath hooks
scripts/link-skills
```

`link-skills` links `AGENTS.md` to `~/.codex/AGENTS.md` and `~/.claude/CLAUDE.md`,
links each skill into `~/.codex/skills/` and `~/.claude/skills/`, and removes
stale links to skills that no longer exist. Run it after adding or removing a
skill.
