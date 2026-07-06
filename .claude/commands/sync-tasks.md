Overwrite a Google Spreadsheet with the current contents of the SOW task board, so teammates and stakeholders have a shareable view without repo access.

## Usage

```
/sync-tasks [sow]
```

`sow` is optional — only needed when the vault has more than one SOW.

---

## Important constraint

The Google Drive MCP has no way to update an existing file's content in place — only `create_file` (new file) and `copy_file` (duplicate). So this skill does **not** overwrite the spreadsheet in place. Every run **creates a brand-new spreadsheet** with a new file ID and a new link, and the old one is left behind in Drive.

This means the shareable link changes on every sync. Always report the new link at the end and remind the user to re-share it and to trash the old file manually.

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

Read `sows/<sow>/sow.config.yaml`. Extract `DRIVE_FOLDERS` and `TASK_BOARD_SHEET_ID` (and `TASK_BOARD_SHEET_URL` if present).

If `DRIVE_FOLDERS` is empty, ask:
> "No Drive folder configured for <sow>. Paste a Google Drive folder URL where the task board spreadsheet should live."

Parse `DRIVE_FOLDERS` as comma-separated URLs and take the **first** one. Extract its folder ID (last path segment after `/folders/`) — this is the `parentId` for the new spreadsheet.

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

### 2 — Create the new spreadsheet

Use the Google Drive MCP `create_file` tool:
- `title`: `<SOW name> Task Board — YYYY-MM-DD` (today's date)
- `textContent`: the CSV built above
- `contentMimeType`: `text/csv`
- `parentId`: the folder ID from pre-flight step 3

Leave `disableConversionToGoogleType` unset (default) so Drive converts the CSV upload into a native Google Sheet.

### 3 — Update sow.config.yaml

Write the new file's ID to `TASK_BOARD_SHEET_ID` and its Drive URL to `TASK_BOARD_SHEET_URL` in `sows/<sow>/sow.config.yaml`, replacing whatever was there before.

### 4 — Report

```
✓ Synced task board for <sow>
  New spreadsheet: <new-url>

Heads up:
- This is a new file — share permissions from the old spreadsheet did NOT carry over. Re-share the link above with anyone who needs access.
- The previous spreadsheet (<old-url>, if one existed) is still in Drive — trash it manually if you don't want duplicates piling up.
```

If `TASK_BOARD_SHEET_URL` was empty before this run (first sync), omit the "previous spreadsheet" line.
