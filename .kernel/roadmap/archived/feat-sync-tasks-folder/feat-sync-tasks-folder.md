---
status: done
priority: medium
owner: ""
phase: ""
depends_on: [feat-sync-tasks]
---

# Feature: Dedicated Task Board Folder Config

## One-Line Overview
Add a `TASK_BOARD_FOLDER_ID` field to `sow.config.yaml` so `/sync-tasks` always drops spreadsheets into a Loka-internal folder, never accidentally into a client-visible Drive folder.

## What's the idea

`/sync-tasks` currently uses `DRIVE_FOLDERS[0]` as the parent folder for new task board spreadsheets. `DRIVE_FOLDERS` is configured for meeting notes — it typically points at a folder shared with the client. This means every `/sync-tasks` run drops an internal task board (with internal notes, owner names, and candid status) into a folder the client can see.

The fix is a dedicated `TASK_BOARD_FOLDER_ID` field in `sow.config.yaml` that `/sync-tasks` uses exclusively. It's separate from `DRIVE_FOLDERS`, so the task board and meeting notes can live in different places — which they almost always should.

### What changes

**`sow.config.yaml` template** (`sows/_template/sow.config.yaml`):

```yaml
# Google Drive folder ID where /sync-tasks drops task board snapshots.
# Should be a Loka-internal folder, NOT one shared with the client.
# If empty, /sync-tasks will ask for a folder URL before proceeding.
TASK_BOARD_FOLDER_ID: ""
```

**`/sync-tasks` skill** (`.claude/commands/sync-tasks.md`):

- Pre-flight: read `TASK_BOARD_FOLDER_ID` from `sow.config.yaml` instead of `DRIVE_FOLDERS[0]`
- If `TASK_BOARD_FOLDER_ID` is empty, prompt: "No task board folder configured for `<sow>`. Paste a Google Drive folder URL for the task board (use a Loka-internal folder, not one shared with the client)." Extract the folder ID and write it to `sow.config.yaml` before proceeding.
- Everything else in the skill stays the same.

### Migration for existing instances

Existing repos already have `TASK_BOARD_FOLDER_ID: ""` (if they ran the upgrade script after `feat-sync-tasks` shipped). On first `/sync-tasks` run after this change, the skill will prompt for the folder — the user pastes the internal folder URL, it gets saved, and all future syncs use it automatically.

## Expected advantages / benefits

- Task board snapshots never land in a client-visible folder by accident
- `DRIVE_FOLDERS` stays focused on meeting notes; task board has its own config
- Empty `TASK_BOARD_FOLDER_ID` prompts the user rather than silently falling back to the wrong folder
- Existing instances self-configure on first use — no manual migration step

## Downsides / risks

- Existing repos need to set `TASK_BOARD_FOLDER_ID` on first run — slight friction, but the prompt handles it
- If someone sets `TASK_BOARD_FOLDER_ID` to a client-shared folder, the problem recurs — no guardrail beyond the config comment

## Test Plan

- `sows/_template/sow.config.yaml` contains the `TASK_BOARD_FOLDER_ID` field.
- `.claude/commands/sync-tasks.md` reads `TASK_BOARD_FOLDER_ID` (not `DRIVE_FOLDERS[0]`) to derive the spreadsheet's `parentId`, and contains the prompt copy for when it's empty.
- `.kernel/upgrade.sh` backfills `TASK_BOARD_FOLDER_ID: ""` into existing `sows/<sow>/sow.config.yaml` files that don't already have it (synthetic tempdir test: a SOW config without the field gets it appended; a SOW config that already has it is left untouched; `sows/_template` is not touched by the backfill loop since it's already covered by the plain file copy).
- Edge cases: empty `TASK_BOARD_FOLDER_ID` with a value present triggers no prompt; a config file missing the field entirely is treated the same as an empty field for backfill purposes.

## Implementation steps

1. Add `TASK_BOARD_FOLDER_ID: ""` (with comment) to `sows/_template/sow.config.yaml`
2. Update `upgrade.sh` to backfill `TASK_BOARD_FOLDER_ID: ""` into existing `sow.config.yaml` files (same pattern used for `TASK_BOARD_SHEET_ID`)
3. Update `.claude/commands/sync-tasks.md` pre-flight: read `TASK_BOARD_FOLDER_ID`; if empty, prompt and save; use it as `parentId`
4. Update `README.md` or skill docs to note the folder separation

## Origin

Discovered in health-edge-ai-2ndbrain (HealthEdge SOW ODS, Jul 2026). `/sync-tasks` dropped the task board into the HE-shared meeting notes folder. The sheet had to be manually trashed and recreated in a Loka-internal folder.
