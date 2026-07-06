Publish the current SOW task board to Google Sheets as a dated snapshot, so teammates and stakeholders have a shareable view without repo access.

## Usage

```
/sync-tasks [sow]
```

`sow` is optional — only needed when the vault has more than one SOW.

---

## Important constraint

The Google Drive MCP has no way to update an existing file's content in place — only `create_file` (new file) and `copy_file` (duplicate). So this skill does **not** overwrite a spreadsheet in place. Every run **creates a brand-new spreadsheet**, titled with today's date, and leaves prior syncs alone in Drive.

Rather than fight this, lean into it: each sync is a dated snapshot of task status at that moment, not a single continuously-updated sheet. The shareable link changes on every sync — always report the new link and remind the user to re-share it. Older snapshots are left in Drive intentionally as history, not clutter to clean up.

---

## Pre-flight

### 1 — Check Google Drive connector

Attempt to list Google Drive tools. If the connector is not available, print:

> "⚠ Google Drive connector not found. To use this command, enable the Google Drive connector in your Claude settings, then restart your session."

Stop here.

### 2 — Resolve the SOW

- Scan `sows/` for subdirectories excluding `_template`.
- If a SOW name was passed as an argument, use it.
- If only one SOW exists, use it.
- If multiple SOWs exist and none was specified, ask: "Which SOW are you syncing the task board for? [list options]"

### 3 — Read SOW config

Read `sows/<sow>/sow.config.yaml`. Extract `TASK_BOARD_FOLDER_ID` and `TASK_BOARD_SHEET_URL` (the link to the most recent snapshot, if any).

`TASK_BOARD_FOLDER_ID` is a dedicated, Loka-internal Drive folder for task board snapshots — deliberately separate from `DRIVE_FOLDERS`, which is configured for meeting notes and often points at a folder shared with the client. Never fall back to `DRIVE_FOLDERS` for this.

If `TASK_BOARD_FOLDER_ID` is empty, ask:
> "No task board folder configured for `<sow>`. Paste a Google Drive folder URL for the task board (use a Loka-internal folder, not one shared with the client)."

Extract the folder ID from the pasted URL (last path segment after `/folders/`) and write it to `TASK_BOARD_FOLDER_ID` in `sows/<sow>/sow.config.yaml` before proceeding. This is the `parentId` for the new spreadsheet.

---

## Sync

### 1 — Read and parse the task board

Read `sows/<sow>/<sow>-tasks.md`. Find the markdown table (header row, separator row of dashes, then data rows).

Convert to CSV:
- Header row → CSV header, in the same column order (`ID,Task,Owner,Priority,Due,Session,Status,Notes`)
- Skip the `|---|---|...` separator row
- For each data row: split on `|`, drop the empty leading/trailing cells from the outer pipes, trim whitespace from each cell
- CSV-escape each cell: if it contains a comma, double-quote, or newline, wrap it in double quotes and double any embedded double quotes
- Join cells with commas, rows with newlines

If the table has no data rows (empty task board), still produce a CSV with just the header row.

### 2 — Create the new snapshot spreadsheet

Use the Google Drive MCP `create_file` tool:
- `title`: `<SOW name> Task Board — YYYY-MM-DD` (today's date — this is what makes it a dated snapshot, not just a new file)
- `textContent`: the CSV built above
- `contentMimeType`: `text/csv`
- `parentId`: the folder ID from pre-flight step 3

Leave `disableConversionToGoogleType` unset (default) so Drive converts the CSV upload into a native Google Sheet.

If a spreadsheet with the same title (i.e. a sync already ran today) already exists in that folder, still create a new one — don't try to reuse or update it. Multiple snapshots on the same day are fine; Drive's own "created" timestamp disambiguates them.

### 3 — Update sow.config.yaml

Write the new file's ID to `TASK_BOARD_SHEET_ID` and its Drive URL to `TASK_BOARD_SHEET_URL` in `sows/<sow>/sow.config.yaml` — these always point at the **latest** snapshot, not a single persistent sheet.

### 4 — Report

```
✓ Synced task board for <sow>
  Snapshot: <new-url> (dated YYYY-MM-DD)

Heads up:
- This is a new file — share permissions from the previous snapshot did NOT carry over. Re-share the link above with anyone who needs access.
- Older snapshots stay in Drive as history — that's intentional, not a mess to clean up.
```
