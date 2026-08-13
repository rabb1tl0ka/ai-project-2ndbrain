---
status: done
priority: medium
owner: ""
phase: ""
depends_on: []
---

# Challenge: SOW tasks live in a table (brittle, hard to parse, merge-conflict-prone) instead of one file per task

## One-Line Overview

`sows/<sow-name>/<sow-name>-tasks.md` stores every open task as a row in one shared markdown table — a format that's harder to parse than checkboxes, prone to merge conflicts across contributors, and can't hold per-task notes or resolution history. The root fix is storage, not reporting: move to one file per task (frontmatter, like `.kernel/roadmap/` items already do), which also makes unified task visibility across meetings and SOW tasks trivial as a side effect.

## The problem

Two related but distinct issues, previously conflated:

1. **Visibility**: no single command shows a user everything they need to work on — checkbox actions and SOW task-table rows are two separate sources (see history below).
2. **Storage** (the actual root cause): SOW tasks are stored as rows in one big table per SOW. That format:
   - Is genuinely harder to parse reliably than checkboxes or frontmatter (arbitrary column order, table dialects, escaping `|` inside cells)
   - Can only express status as a flat cell value (`open`/`blocked`) — no room for a resolution note, a history of status changes, or why something got closed
   - Puts every contributor's task edits into the same file, which is exactly the merge-conflict shape this repo's own branch model (per-person branches → SOW integration branch → main) is designed to avoid elsewhere
   - Was chosen for one specific reason: `/sync-tasks` exports it straight into a Google Sheet, and a table maps 1:1 onto spreadsheet rows. That's a real constraint, but it's a reporting/export need, not a reason the *source of truth* has to be a table.

This template already has a working precedent for the better format: `.kernel/roadmap/<item>/<item>.md` — one file per item, YAML frontmatter (`status`, `priority`, `owner`, `phase`, `depends_on`) plus a markdown body for full context. Frontmatter is trivial and robust to parse (no column-order ambiguity), supports real status fields, and each item's file can carry as much narrative as it needs (see `challenge-client-deliverables.md` for how rich that body gets). There's no structural reason SOW tasks couldn't use the same shape: `sows/<sow-name>/tasks/<task-id>.md`.

If storage moves to per-task files, the visibility problem in this doc's earlier version (see below) gets much easier: a unified "what do I need to work on" skill just globs frontmatter across `sows/*/tasks/*.md` — no table-parsing brittleness to work around, no lossy merge between a checkbox line and a table row.

## Options

### 1. Migrate SOW tasks to one file per task, frontmatter-based (recommended)

`sows/<sow-name>/tasks/<task-id>.md`, frontmatter mirrors the current table schema (`owner`, `priority`, `due`, `session`, `status`), body holds a free-text description plus a running notes/resolution log. Closed tasks move to `sows/<sow-name>/tasks/done/` (or get a `status: done` field) instead of a separate weekly done log.

**Pros:**
- Same format this repo already trusts for roadmap items — no new pattern to invent or teach
- Frontmatter parsing is robust; kills the table-brittleness problem at the root instead of working around it
- Per-task files mean per-task git history — clean diffs, far fewer merge conflicts when multiple contributors touch different tasks on their own branches
- Room for real content: resolution notes, links, a timeline — not just a status cell
- Makes a unified visibility skill (checkbox actions + SOW tasks) much simpler to build, since both sources become "structured markdown files to glob," not "two incompatible shapes to merge"

**Cons:**
- `/sync-tasks` needs a rewrite: glob + parse frontmatter across files → build the sheet, instead of read-one-table → push. More code than today, though each piece is simpler
- Migration path needed for any already-onboarded engagement repo currently using the table (this template repo itself has none yet — only `sows/_template/sow-tasks.md` — but downstream repos built from earlier template versions do)
- Directory of many small files is less "open one file, see everything at a glance" than a table — mitigated by the visibility skill in option 2, but that becomes a dependency rather than a nice-to-have
- `meeting-recap.md`'s "Task board review" step needs its ADD/CLOSE/UPDATE diff logic rewritten against files instead of table rows

### 2. Unified "my tasks" skill on top of (either) storage format

Independent of storage: a skill that reads both checkbox actions and SOW tasks and reports them together. Feasible today against the table (with parsing brittleness) or trivially easy after option 1 lands.

**Pros:** directly answers "what do I need to work on"; can ship incrementally against the current table and get simpler later once option 1 lands
**Cons:** built against the table today, it inherits all the table's parsing brittleness — likely rework once storage changes

### 3. Keep the table, teach `/action-board` to parse it directly

Rejected in the earlier version of this doc and still rejected: couples a deliberately generic, portable skill to this vault's specific (and brittle) table schema. Doesn't address the underlying storage problem either.

## Feature spec

Option 1 is specced out in `feat-sow-tasks-as-files.md`.

## Recommendation

Do option 1 first — it's the antifragile fix (root cause: wrong storage format, not "two skills don't talk to each other"). Once tasks are per-file, build option 2 (unified visibility skill) as a thin follow-on — it becomes close to free once both sources are structured markdown files. Don't do option 3.

Sequencing matters here: shipping option 2 against the current table first would mean rebuilding it once option 1 lands. Worth confirming there's no hard blocker (e.g. how many downstream repos already have populated task tables that would need migrating) before committing to option 1 as the first move.

## Test Plan

- New task files created with correct frontmatter schema (`owner`, `priority`, `due`, `session`, `status`) matching today's table columns
- `/sync-tasks` correctly builds a spreadsheet-equivalent view by reading all task files for a SOW (same output shape as today's table export)
- `meeting-recap`'s task board review step creates/updates/closes task files instead of table rows, with the same dedup guarantees (no false-positive re-adds of already-closed items)
- A migration script/checklist converts an existing populated `<sow>-tasks.md` table into individual task files without losing any row's data
- (Follow-on, after storage lands) unified visibility skill correctly aggregates checkbox actions and SOW task files into one report, labeled by source
