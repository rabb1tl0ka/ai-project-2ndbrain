---
status: done
priority: medium
owner: ""
phase: ""
depends_on: []
---

# Feature: Bundle github-commit, github-branch-publish, github-branch-refresh in the template

## One-Line Overview
Move `github-commit`, `github-branch-publish`, and `github-branch-refresh` from the external `claude-skills` clone-at-bootstrap-time flow into `.claude/skills/` in this template repo, so every fork gets them at clone time with no network dependency.

## What's the idea

`/bootstrap` currently clones `github.com/rabb1tl0ka/claude-skills` at runtime and copies `action-board`, `github-commit`, and `github-branch-publish` into the new fork's `.claude/skills/`. `github-branch-refresh` was never added to that clone list or to `claude-skills` at all — it only existed inside one fork (`ai-design-cards`).

Bundling these three directly into the template removes a network dependency from `/bootstrap` for them, and puts them under the same versioning/upgrade path as the rest of the template's tooling. `action-board` stays on the external `claude-skills` clone path — it's out of scope here.

## Expected advantages / benefits

- `/bootstrap` no longer depends on network access to a second repo for these 3 skills
- New forks get them automatically with the template checkout
- Existing forks pick up new/changed bundled skills via `/upgrade --apply`
- One less repo to keep in sync for skill updates

## Downsides / risks

- `action-board` stays on the old clone-from-`claude-skills` path, so the template now has two different skill-distribution mechanisms — worth consolidating fully in a follow-up
- `/upgrade` blind-checks-out `.claude/skills/`, so a fork's local hand-edits to these 3 skills would be silently overwritten on upgrade (same tradeoff `/upgrade` already accepts for commands/templates)

## What's been tried already

The three skills were authored and iterated on inside the `ai-design-cards` fork's `.claude/skills/`. This item moves the finished versions upstream into the template.

## Implementation steps

1. Copy `.claude/skills/{github-commit,github-branch-publish,github-branch-refresh}/SKILL.md` into this repo's `.claude/skills/`
2. Update `bootstrap.md`'s skill-fetch step to drop `github-commit` and `github-branch-publish` from the `claude-skills` clone (leave `action-board`)
3. Update `upgrade.md` step 4b to check out `.claude/skills/` from the template remote, and step 4d to stage it
4. Update `README.md`'s description of what `/bootstrap` pulls from `claude-skills` (now just `action-board`)
5. Add test coverage in `.kernel/test.py`

## Test Plan

- `.claude/skills/github-commit/SKILL.md`, `.claude/skills/github-branch-publish/SKILL.md`, and `.claude/skills/github-branch-refresh/SKILL.md` all exist in this repo
- `bootstrap.md` no longer references cloning `github-commit` or `github-branch-publish` from `claude-skills`, but still references `action-board`
- `upgrade.md`'s file/dir checkout list includes `.claude/skills/`

## Origin
Requested directly by Bruno: move the three GitHub-workflow skills out of the `ai-design-cards` fork and into the template so all forks get them.
