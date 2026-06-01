---
status: in-progress
priority: high
owner: "@brunocoelho"
phase: ""
depends_on: []
---

# Feature: Notion Channel

## One-Line Overview
Bidirectional Notion integration that lets users publish SOW artifacts to Notion and ingest existing Notion pages as a data source during bootstrap.

## What this is

A read/write data channel between the project 2nd brain and a per-SOW Notion project page.

**Write direction:** `/publish-to-notion <file>` publishes any `.md` file in the vault as a Notion child page under the SOW's configured project page. Idempotent via title-matching — republishing updates the existing page rather than creating a duplicate.

**Read direction:** `/bootstrap` ingests existing child pages from the SOW's Notion project page as a data source, alongside Slack and Google Drive.

## Design decisions

- `NOTION_PROJECT_URL` lives in `sows/<sow>/sow.config.yaml` — per SOW, not global
- Idempotency via title-match (filename without `.md`), no ID storage in config
- Notion MCP connector is a hard pre-requisite — graceful warning if not found, no exception
- Notion is treated as a final artifacts layer, not a sync target — no two-way conflict resolution needed

## Scope

- `sow.config.yaml` template: add `NOTION_PROJECT_URL` field
- New command: `project-vault/.claude/commands/publish-to-notion.md`
- Updated command: `project-vault/.claude/commands/bootstrap.md` — Section E: Notion channel
- Updated command: `.claude/commands/2ndbrain.md` — show Notion URL status per SOW

## Open questions

1. Should `/publish-to-notion` support publishing an entire SOW directory in one call, or file-by-file only for now?
2. What happens when `NOTION_PROJECT_URL` is set but the page has been deleted in Notion?
