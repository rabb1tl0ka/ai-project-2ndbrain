# Roadmap — ai-project-2ndbrain (repo tooling)

Ideas, challenges, and features for the template repo itself.

## Current roadmap

(The table above is automatically maintained by Claude Code. Do not edit it manually.)

| File | Phase | Status | Priority | Deps | Owner | One-Line Overview |
|------|-------|--------|----------|------|-------|-------------------|
| [feat-notion-channel](feat-notion-channel/feat-notion-channel.md) | | 🚧 in-progress | high | | @brunocoelho | Bidirectional Notion integration that lets users publish SOW artifacts to Notion and ingest existing Notion pages as a data source during bootstrap. |
| [feat-sow-branch-config](archived/feat-sow-branch-config/feat-sow-branch-config.md) | | ✅ done | high | | | `/onboard` asks for the SOW lead, writes `sow_lead` to `sow.config.yaml`, and creates the long-lived `sow{N}` branch on GitHub with a suggestion to protect it. |
| [feat-sow-task-board](archived/feat-sow-task-board/feat-sow-task-board.md) | | ✅ done | high | | | Per-SOW task board with priority inference, weekly done log, and per-SOW CLAUDE.md rules for session-start auto-load and TLU generation. |
| [feat-tlu-generation](feat-tlu-generation/feat-tlu-generation.md) | | ⏳ todo | medium | | | Every SOW gets a `TLUs/` output folder and a `templates/tlu-template.md`, with CLAUDE.md instructions that tell Claude how to generate a weekly Traffic Light Update for the Sales Lead from the SOW's working notes and meeting summaries. |
| [feat-sync-tasks](archived/feat-sync-tasks/feat-sync-tasks.md) | | ✅ done | medium | | | A `/sync-tasks` skill that recreates a Google Spreadsheet from the current SOW task board markdown on demand (Drive MCP can't overwrite in place, so each sync produces a new shareable link). |
| [feat-sync-tasks-folder](archived/feat-sync-tasks-folder/feat-sync-tasks-folder.md) | | ✅ done | medium | feat-sync-tasks | | Add a `TASK_BOARD_FOLDER_ID` field to `sow.config.yaml` so `/sync-tasks` always drops spreadsheets into a Loka-internal folder, never accidentally into a client-visible Drive folder. |
| [challenge-client-deliverables](challenge-client-deliverables/challenge-client-deliverables.md) | | ⏳ todo | high | | | Without a clear structural boundary between internal working files and client-facing outputs, any file in a working session directory is one accidental attachment away from a client. |
| [challenge-template-data-migration](challenge-template-data-migration/challenge-template-data-migration.md) | | ⏳ todo | medium | | | upgrade.sh copies structural changes but can't backfill new fields into existing user sow.config.yaml files — needs a migration mechanism. |
| [idea-test-suite-splitting](idea-test-suite-splitting/idea-test-suite-splitting.md) | | 💡 idea | low | | | Split test.py into focused files per skill as the suite grows — revisit when test.py exceeds ~400 lines. |
