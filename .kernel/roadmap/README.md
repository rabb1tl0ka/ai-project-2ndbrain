# Roadmap — ai-project-2ndbrain (repo tooling)

Ideas, challenges, and features for the template repo itself.

## Current roadmap

(The table above is automatically maintained by Claude Code. Do not edit it manually.)

| File | Phase | Status | Priority | Deps | Owner | One-Line Overview |
|------|-------|--------|----------|------|-------|-------------------|
| [feat-notion-channel](feat-notion-channel/feat-notion-channel.md) | | 🚧 in-progress | high | | @brunocoelho | Bidirectional Notion integration that lets users publish SOW artifacts to Notion and ingest existing Notion pages as a data source during bootstrap. |
| [feat-sow-branch-config](archived/feat-sow-branch-config/feat-sow-branch-config.md) | | ✅ done | high | | | `/onboard` asks for the SOW lead, writes `sow_lead` to `sow.config.yaml`, and creates the long-lived `sow{N}` branch on GitHub with a suggestion to protect it. |
| [feat-sow-task-board](feat-sow-task-board/feat-sow-task-board.md) | | ⏳ todo | high | | | A Claude-maintained task board per SOW that tracks open items across all stakeholders, prunes completed tasks into a weekly done log, and keeps Claude automatically aware of who owes what at every session start. |
| [feat-tlu-generation](feat-tlu-generation/feat-tlu-generation.md) | | ⏳ todo | medium | | | Every SOW gets a `TLUs/` output folder and a `templates/tlu-template.md`, with CLAUDE.md instructions that tell Claude how to generate a weekly Traffic Light Update for the Sales Lead from the SOW's working notes and meeting summaries. |
| [challenge-client-deliverables](challenge-client-deliverables/challenge-client-deliverables.md) | | ⏳ todo | high | | | Without a clear structural boundary between internal working files and client-facing outputs, any file in a working session directory is one accidental attachment away from a client. |
| [challenge-template-data-migration](challenge-template-data-migration/challenge-template-data-migration.md) | | ⏳ todo | medium | | | upgrade.sh copies structural changes but can't backfill new fields into existing user sow.config.yaml files — needs a migration mechanism. |
| [idea-test-suite-splitting](idea-test-suite-splitting/idea-test-suite-splitting.md) | | 💡 idea | low | | | Split test.py into focused files per skill as the suite grows — revisit when test.py exceeds ~400 lines. |
