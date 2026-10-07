# Writing Skills

A skill is a small, reusable workflow an agent loads on demand. Every skill must
earn its place: it exists because a real task needed it, and it stays only while
it keeps changing outcomes.

## Shape

```text
skills/<name>/
  SKILL.md        required; under 100 lines is the target, 150 is the limit
  scripts/        deterministic steps the skill runs
  references/     long prompts, rubrics, and templates loaded by pointer
  assets/         files the skill ships, such as images
```

Skills are plain Markdown so they work in both Codex and Claude Code. Do not add
harness-specific files unless a real need appears.

## Front matter

```yaml
---
name: backend-health            # same as the folder, kebab-case
description: "Check production health ... Use when ..."
---
```

The description is loaded into every session, so it is routing, not
documentation. Say what the skill does and when to use it in 300 characters or
fewer. Put trigger words there, because the body loads only after the skill is
chosen.

## Body

1. One line of purpose.
2. **Use when / Not for** — the boundary, including when to stay direct.
3. **Steps** — numbered, each ending with a concrete `Done when:` condition.
4. **Output** — a fixed template so results are comparable run to run.
5. **Guardrails** — only the hard stops that matter for this skill.

Write what to do, not what to avoid. Explain the reason behind any rule that is
not obvious, and date rules that came from an incident. Cut any instruction the
agent already follows without being told.

## Scripts over prose

If a step is the same every time, put it in `scripts/`, make it exit non-zero on
failure, and tell the agent to run it. Commands written in prose drift; scripts
can be tested.

## Composition

Call another skill by name ("use the `reflect` skill"), never by a file path into
another skill's folder.

## Proof and safety

- Each skill defines what evidence closes its work. Missing evidence is
  `UNKNOWN`, never success.
- Never print credentials, tokens, or patient data. Redact them in output.
- Sending, publishing, merging, deploying, spending, and production changes need
  explicit approval unless the skill says otherwise and the user agreed to it.

## Changing a skill

- Change a skill only for an observed failure or a proven improvement, not a
  hypothetical one.
- Prefer turning a lesson into a script, test, or check over adding more prose.
- After editing, run `scripts/validate-skills` and `scripts/link-skills`.
