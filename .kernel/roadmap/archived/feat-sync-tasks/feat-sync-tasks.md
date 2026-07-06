---
status: done
priority: medium
owner: ""
phase: ""
depends_on: []
---

# Feature: /sync-tasks Skill

## One-Line Overview
A `/sync-tasks` skill that overwrites a Google Spreadsheet with the current contents of the SOW task board markdown file, keeping a shareable view in sync with the source of truth on demand.

## What's the idea

The SOW task board lives in `sows/<sow>/<sow>-tasks.md` — Claude maintains it as the source of truth. But teammates and stakeholders need a shareable, readable view without needing to open the repo. A Google Spreadsheet fills that role.

The problem is keeping them in sync. Auto-sync on every task board change is fragile (Drive MCP not always available, silent failures). The right model is an explicit trigger: the user says `/sync-tasks` and Claude overwrites the spreadsheet with the current task board state.

### How it works

**Implementation note:** the Google Drive MCP available in this environment has no tool to overwrite an existing file's content or delete a file — only `create_file` (new file) and `copy_file` (duplicate). True in-place overwrite, as originally envisioned below, isn't possible with these tools. Confirmed with the user (2026-07-06); the accepted approach is "recreate as a dated snapshot on every sync" — reframed from a workaround into the actual design (2026-07-06, after living with it in practice): each sync is a dated spreadsheet capturing task status at that moment, not one continuously-updated sheet.

1. User runs `/sync-tasks` (optionally with a SOW name if multiple SOWs exist)
2. Skill reads `sows/<sow>/<sow>-tasks.md`
3. Parses the markdown table into CSV rows
4. Reads `TASK_BOARD_SHEET_ID` / `TASK_BOARD_SHEET_URL` from `sows/<sow>/sow.config.yaml` (previous run's spreadsheet, if any)
5. Creates a **new** Google Spreadsheet via Google Drive MCP (`create_file` with CSV content, auto-converted to Sheets) — cannot overwrite the previous one in place
6. Writes the new file's ID and URL back to `sow.config.yaml`
7. Responds with the new link, and reminds the user to re-share it and trash the old spreadsheet manually

### Config

Add to `sow.config.yaml`:

```yaml
# Google Drive file ID of the current task board spreadsheet, written by /sync-tasks.
# Each /sync-tasks run creates a NEW spreadsheet (the Drive MCP can't overwrite file
# content in place) and overwrites this ID — do not edit by hand.
TASK_BOARD_SHEET_ID: ""

# Shareable link to the current task board spreadsheet, written by /sync-tasks.
# Changes on every sync — re-share this link with stakeholders after each run.
TASK_BOARD_SHEET_URL: ""
```

Every run (first or subsequent) creates a new spreadsheet in `DRIVE_FOLDERS[0]` and overwrites both fields.

### Skill location

`.claude/commands/sync-tasks.md` at the repo root — available to all SOWs.

## Expected advantages / benefits

- Teammates and stakeholders get a live-ish shareable view without repo access
- One source of truth (the markdown file) — spreadsheet is always derived, never edited directly
- Explicit trigger means no silent failures; user knows when it ran and whether it succeeded
- First-run auto-creates the spreadsheet and saves the ID — zero manual setup after that
- Follows the established skill pattern already used by `/meeting-recap`, `/bootstrap`, `/onboard`

## Downsides / risks

- The spreadsheet link changes on every sync (a new file is created each time, since the Drive MCP can't overwrite in place) — the user must re-share the new link each time. Reframed as a dated-snapshot feature rather than fought as a bug, this is now an accepted tradeoff, not a defect.
- Drive MCP must be available in the session — skill fails gracefully if not, but can't auto-recover
- If multiple SOWs exist and user doesn't specify, skill must ask which SOW — minor friction
- Old snapshots accumulate in Drive over time — intentional (history), but worth knowing if Drive storage/clutter ever becomes a concern

## Implementation steps

1. Add `TASK_BOARD_SHEET_ID: ""` and `TASK_BOARD_SHEET_URL: ""` to `sow.config.yaml` template (in `sows/_template/sow.config.yaml`)
2. Create `.claude/commands/sync-tasks.md` with the skill spec:
   - Pre-flight: determine SOW, check Drive MCP connector, read `sow.config.yaml`, resolve the target Drive folder
   - Read and parse `<sow>-tasks.md` markdown table → CSV
   - Create a new spreadsheet via Drive MCP `create_file`, save the new ID/URL to `sow.config.yaml`
   - Confirm with the new link and a reminder to re-share / trash the old file
3. Update root `CLAUDE.md` to document the `/sync-tasks` trigger and the recreate-on-sync behavior
4. Add tests to `.kernel/test.py`: config template fields, markdown-table-to-CSV parsing (including comma/quote escaping and empty task boards)

## Test Plan

- `sow.config.yaml` template has `TASK_BOARD_SHEET_ID` and `TASK_BOARD_SHEET_URL` fields, both empty by default
- `.claude/commands/sync-tasks.md` exists and documents: the recreate-per-sync behavior, the pre-flight Drive connector check, and the CSV parsing algorithm
- Markdown table → CSV parsing, tested directly (no live Drive call in the test suite):
  - Header row converts correctly, separator row (`|---|---|`) is skipped
  - A normal data row parses into the right number of comma-separated fields
  - A cell containing a comma is wrapped in double quotes
  - A cell containing a double quote has the quote doubled and the cell wrapped in quotes
  - An empty task board (header + separator, no data rows) produces a CSV with only the header row, not a crash

## Origin

First identified during health-edge-ai-2ndbrain (HealthEdge SOW ODS, Jul 2026). Task board was manually exported to a Google Spreadsheet — user wanted a way to keep it in sync without friction. The explicit trigger pattern (`/sync-tasks`) was chosen over auto-sync to avoid silent Drive MCP failures.
