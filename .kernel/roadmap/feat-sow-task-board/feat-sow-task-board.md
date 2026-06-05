---
status: in-progress
priority: high
owner: ""
phase: ""
depends_on: []
---

# Feature: SOW Task Board

## One-Line Overview

A Claude-maintained task board per SOW — scoped to `sows/<sow>/` — that tracks open items across all stakeholders, prunes completed tasks into a weekly done log, and keeps Claude automatically aware of who owes what at every session start.

## What this is

A lightweight, Claude-owned task tracking system living at the SOW level. It gives Claude full situational awareness of open tasks — across the Loka team, client side, and everyone in between — without requiring manual curation from the user.

Two files, one convention per SOW:

**`<sow>-tasks.md`** (at `sows/<sow>/`) — the live board. Only open items. Claude creates, updates, and prunes this file as tasks surface and close.

**`done/YYYY-WW.md`** (at `sows/<sow>/done/`) — weekly closed task log. When Claude removes a task from `<sow>-tasks.md`, it appends it here before deleting it. One file per ISO week. Doubles as TLU source material.

The `<sow>` prefix on the tasks file (e.g. `sow3-tasks.md`, `sow-ods-tasks.md`) prevents ambiguity when multiple SOW directories are open in a file picker.

## Task schema

Each task is a table row:

| ID | Task | Owner | Priority | Due | Session | Status | Notes |
|----|------|-------|----------|-----|---------|--------|-------|

- `ID`: short slug (e.g. `kickoff-01`)
- `Owner`: person responsible — anyone (Bruno, Rommel, Andrew, etc.)
- `Priority`: `high` | `medium` | `low` — Claude infers from context if not set explicitly
- `Due`: date or empty — leave empty if unknown, don't prompt
- `Session`: which working session this came from (e.g. `kickoff`, `tech-research`)
- `Status`: `open` | `blocked`
- `Notes`: context, blockers, links

Done tasks in `done/YYYY-WW.md` use the same schema plus a `Closed` date column.

## Where the rules live

Each SOW has its own `sows/<sow>/CLAUDE.md` with the task board rules scoped to that SOW. This prevents collision between SOW leads (Ronny's sow3 tasks and Bruno's sow-ods tasks are fully independent).

The root `CLAUDE.md` has a brief pointer: read the SOW's `CLAUDE.md` at session start alongside the SOW reference file.

## Claude behavior (in per-SOW CLAUDE.md)

1. **Session start**: always read `<sow>-tasks.md` before anything else for this SOW
2. **Task surfacing**: whenever a meeting summary, working session, or conversation produces a clear action item with an owner, add it to `<sow>-tasks.md` immediately — don't wait to be asked. Infer priority from context if not stated.
3. **Task closing**: when a task is confirmed done (by the user or implied by context), append it to `done/YYYY-WW.md` (current ISO week) then remove it from `<sow>-tasks.md`
4. **TLU generation**: read `done/YYYY-WW.md` as the primary source for "what shipped this week"
5. **Blocker flagging**: tasks with `status: blocked` always surface in TLUs as CTAs

## What gets created

- `sows/_template/CLAUDE.md` — per-SOW task board rules (placeholder `{{SOW_NAME}}`)
- `sows/_template/sow-tasks.md` — starter template; renamed to `<sow>-tasks.md` by `/onboard`
- `sows/_template/done/.gitkeep` — ensures `done/` directory exists
- `sows/_template/` rename step in `/onboard` — renames `sow-tasks.md` → `<sow>-tasks.md`
- Root `CLAUDE.md` — brief pointer to per-SOW CLAUDE.md at session start

## Design decisions

- Per-SOW `CLAUDE.md` not root — multiple SOW leads each have their own task board with no collision
- `<sow>-tasks.md` naming — unambiguous in file pickers, consistent with `<sow>-reference.md`
- Single tasks file per SOW (not per working session) — unified cross-team view; `session:` tag preserves context
- Weekly done log matches TLU cadence — natural alignment, no extra synthesis step
- Claude owns writes — user just confirms or corrects; no manual entry required
- ISO week naming (`YYYY-WW`) keeps done logs sortable and unambiguous
- Priority inferred by Claude if not set — no friction for the user, still useful signal
- No due date prompting — leave empty if unknown

## Test Plan

- `sows/_template/CLAUDE.md` exists
- `sows/_template/sow-tasks.md` exists with correct schema (ID, Task, Owner, Priority, Due, Session, Status, Notes columns)
- `sows/_template/done/.gitkeep` exists
- `/onboard` step 5a renames `sow-tasks.md` → `<sow>-tasks.md` alongside `sow-reference.md`
- `sow-tasks.md` contains the `Priority` column
- Root `CLAUDE.md` references per-SOW CLAUDE.md at session start
