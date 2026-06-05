---
status: todo
priority: high
owner: ""
phase: ""
depends_on: []
---

# Feature: SOW Task Board

## One-Line Overview
A Claude-maintained task board per SOW that tracks open items across all stakeholders, prunes completed tasks into a weekly done log, and keeps Claude automatically aware of who owes what at every session start.

## What this is

A lightweight, Claude-owned task tracking system living at the SOW level. It gives Claude full situational awareness of open tasks — across the Loka team, client side, and everyone in between — without requiring manual curation from the user.

Two files, one convention:

**`tasks.md`** (at `sows/<sow>/`) — the live board. Only open items. Claude creates, updates, and prunes this file as tasks surface and close.

**`done/YYYY-WW.md`** (at `sows/<sow>/done/`) — weekly closed task log. When Claude removes a task from `tasks.md`, it appends it here before deleting it. One file per ISO week. Doubles as TLU source material.

## Task schema

Each task in `tasks.md` is a table row:

| ID | Task | Owner | Due | Session | Status | Notes |
|----|------|-------|-----|---------|--------|-------|

- `ID`: short slug (e.g. `kickoff-01`)
- `Owner`: person responsible — can be anyone (Bruno, Rommel, Andrew, etc.)
- `Due`: date or empty
- `Session`: which working session this came from (e.g. `kickoff`, `tech-research`)
- `Status`: `open` | `blocked`
- `Notes`: context, blockers, links

Done tasks in `done/YYYY-WW.md` use the same schema plus a `Closed` date column.

## Claude behavior

These rules live in `sows/<sow>/CLAUDE.md`:

1. **Session start**: always read `tasks.md` before anything else
2. **Task surfacing**: whenever a meeting summary, working session, or conversation produces a clear action item with an owner, add it to `tasks.md` immediately — don't wait to be asked
3. **Task closing**: when a task is confirmed done (by the user or implied by context), append it to the current week's `done/YYYY-WW.md` then remove it from `tasks.md`
4. **TLU generation**: read the current week's `done/YYYY-WW.md` as the primary source for "what shipped this week"
5. **Blocker flagging**: tasks with `status: blocked` always surface in TLUs as CTAs

## Scope

- `project-vault/sows/_template/tasks.md` — starter template with schema header and example row (commented out)
- `project-vault/sows/_template/done/` — empty directory with `.gitkeep`
- `project-vault/sows/_template/CLAUDE.md` — add session-start auto-load rule and close/archive behavior
- `project-vault/.claude/commands/tlu.md` — reference `done/YYYY-WW.md` as primary weekly input
- `README.md` — document `tasks.md` and `done/` in the SOW structure table

## Design decisions

- Single `tasks.md` per SOW (not per working session) — unified cross-team view is more valuable than colocation
- `session:` tag on each task preserves the "close to context" benefit without splitting the file
- Weekly done log matches TLU cadence — natural alignment, no extra synthesis step
- Claude owns writes — user just confirms or corrects; no manual entry required
- ISO week naming (`YYYY-WW`) keeps done logs sortable and unambiguous

## Open questions

1. Should `tasks.md` include a `priority` column, or is that overkill for this level of tracking?
2. When a task has no clear due date, should Claude prompt the user to set one or leave it empty?
3. Should the done log roll up into a monthly summary at end of month, or is weekly granularity enough for the full SOW lifecycle?
