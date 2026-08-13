---
status: done
priority: medium
owner: ""
phase: ""
depends_on: []
---

# Feature: SOW tasks as individual files instead of a shared table

## One-Line Overview

Replace `sows/<sow-name>/<sow-name>-tasks.md` (one shared markdown table) with `sows/<sow-name>/tasks/<task-id>.md` (one frontmatter file per task) — same schema, robust parsing, per-task git history, and room for a real resolution log instead of a flat status cell.

## Origin

Raised in `challenge-sow-task-board-visibility.md`. That doc's root-cause finding: the table format was chosen only because `/sync-tasks` needed a spreadsheet-shaped export (`feat-sow-task-board`, archived), not because a table is the right source of truth. The table's brittleness (arbitrary column order, dialect issues, one shared file every contributor edits) is what makes cross-source task visibility hard to build well. This feature is the recommended fix — do this first, then the unified "what do I need to work on" visibility skill becomes a thin follow-on once both task sources are structured files.

## What this is

Each task becomes its own file: `sows/<sow-name>/tasks/<task-id>.md`, frontmatter mirrors the current table schema, body holds free-text description plus a running notes/resolution log.

```markdown
---
id: kickoff-01
task: "Confirm data access with client IT"
owner: rommel
priority: high
due: 2026-08-20
session: kickoff
status: open
---

## Notes

Waiting on IT to provision a read-only DB user. Followed up 2026-08-14, no response yet.
```

Closed tasks move to `sows/<sow-name>/tasks/done/<task-id>.md` (frontmatter gains a `closed:` date) instead of being appended to a shared weekly done log — mirrors the `.kernel/roadmap/archived/` pattern already used for template roadmap items.

## What changes

**Scaffold** (`sows/_template/`):
- Remove `sow-tasks.md`
- Add `tasks/.gitkeep` and `tasks/done/.gitkeep`

**`/onboard`**: stop renaming `sow-tasks.md` → `<sow>-tasks.md`; nothing to rename, `tasks/` is already SOW-scoped by directory, not filename.

**Per-SOW `CLAUDE.md`** (task board rules section, from `feat-sow-task-board`):
- Session start: instead of "read `<sow>-tasks.md`", read all files under `sows/<sow>/tasks/*.md` (excluding `done/`)
- Task surfacing: create a new file under `tasks/` instead of appending a table row
- Task closing: move the file to `tasks/done/`, add `closed:` date to frontmatter, instead of copy-then-delete-row into a weekly log

**`/sync-tasks`** (`.claude/commands/sync-tasks.md`): rebuild the spreadsheet by globbing `tasks/*.md` and reading frontmatter into rows, instead of reading one table file. Same spreadsheet output shape — this only changes the read side.

**`/meeting-recap`** (`.claude/commands/meeting-recap.md`, "Task board review" step): the ADD/CLOSE/UPDATE diff logic currently proposed against table rows should propose creating/moving/editing task files instead. Dedup check (against live tasks + current week's done log) becomes: dedup against all files under `tasks/` and `tasks/done/` from the current ISO week.

**Migration for existing SOWs**: a one-time script/checklist that reads a populated `<sow>-tasks.md` table and writes one file per row into `tasks/`, preserving all columns. Needed for any downstream repo that already has open tasks in the old format (this template repo itself has none yet — only the unpopulated `_template` scaffold).

## Expected advantages / benefits

- Frontmatter parsing is robust — no column-order ambiguity, no table-dialect edge cases to defend against
- Per-task files mean per-task git diffs — far fewer merge conflicts when multiple contributors add/edit tasks on their own branches (this repo's own branch model is built around avoiding exactly this kind of shared-file contention)
- Room for real content per task: a resolution note, a timeline of status changes, links — not just a flat status cell
- Sets up the unified "what do I need to work on" visibility skill (checkbox actions + SOW tasks) to be simple: both sources become "glob structured markdown files," no lossy merge between a checkbox line and a table row
- Matches a pattern this repo already trusts (`.kernel/roadmap/<item>/<item>.md`) — no new format to invent or teach

## Downsides / risks

- `/sync-tasks` needs a rewrite (glob + frontmatter parse → build sheet, instead of read-table → push) — more code than today, though each piece is simpler than table parsing
- Directory of many small files loses the "open one file, see everything at a glance" property a table has — real cost until/unless the unified visibility skill exists
- Migration needed for any already-onboarded downstream repo with a populated task table; unknown how many exist or how large their tables are — should be scoped before starting implementation
- `meeting-recap`'s task board review diff format (ADD/CLOSE/UPDATE) needs rework to operate on files instead of rows — not just a find-and-replace, the dedup logic changes shape too

## What's been tried already

The current table format (`feat-sow-task-board`, archived) was a deliberate design choice at the time: "Single tasks file per SOW (not per working session) — unified cross-team view." That reasoning is still valid — this feature preserves the unified-per-SOW view (one `tasks/` directory per SOW), it just changes the storage unit from "one row in a shared file" to "one file," which keeps the unified view while fixing the parsing and merge-conflict problems.

## Open questions

1. Does `tasks/done/` need a size/retention policy over a long engagement, or is per-task-file storage cheap enough that it never matters in practice?
2. Should the migration script run automatically via `upgrade.sh`, or is this disruptive enough (changes the on-disk shape of live task data) that it should always be a manual, confirmed step per SOW?
3. Does `/sync-tasks`'s spreadsheet still sort/group the same way once the source is a glob of files rather than an ordered table — does row order need to be preserved via a frontmatter field (e.g. `created:` date) to keep the exported sheet stable?

## Test Plan

- `sows/_template/tasks/.gitkeep` and `sows/_template/tasks/done/.gitkeep` exist; `sow-tasks.md` is removed from the scaffold
- Creating a task writes a correctly-schemed file to `sows/<sow>/tasks/<task-id>.md`
- Closing a task moves the file to `sows/<sow>/tasks/done/<task-id>.md` with a `closed:` date added
- `/sync-tasks` produces the same spreadsheet shape (columns, open-items-only) as today's table-based export, now sourced from globbing `tasks/*.md`
- `/meeting-recap`'s task board review step creates/moves/edits task files with the same dedup guarantee (no false-positive re-adds of items already closed this week)
- Migration script converts a populated `<sow>-tasks.md` table into one file per row with no data loss, verified against a fixture table with multiple rows including edge cases (empty `Due`, multi-word `Notes` with a `|` character)
- `/onboard` no longer performs the `sow-tasks.md` → `<sow>-tasks.md` rename step
