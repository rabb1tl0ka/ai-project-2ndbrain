---
status: todo
priority: medium
owner: ""
phase: ""
depends_on: []
---

# Challenge: Template upgrades don't backfill existing user data

## One-Line Overview

`upgrade.sh` handles structural changes fine but has no mechanism for backfilling new fields into user-created files it deliberately never touches (e.g. `sows/*/sow.config.yaml`).

## The problem

When a template upgrade introduces a new field in `sows/_template/sow.config.yaml`, the template copy gets the field. But every existing SOW's `sow.config.yaml` doesn't — `upgrade.sh` deliberately skips `sows/` to protect project content.

This is a data migration problem, identical to "added a column to a table, now existing rows don't have it."

### Real example

`feat-sow-branch-config` added `sow_lead` to `sow.config.yaml`. After running `upgrade.sh` on `health-edge-ai-2ndbrain`:
- `sows/_template/sow.config.yaml` ✓ has `sow_lead`
- `sows/sow3/sow.config.yaml` ✗ missing `sow_lead` — had to be added manually
- `sows/sow-ods/sow.config.yaml` ✗ missing `sow_lead` — had to be added manually

At one or two repos this is a quick manual fix. At ten repos, it's error-prone and easy to miss.

## Options

### 1. Migration checklist printed by upgrade.sh (low effort)

After copying files, upgrade.sh prints a "Manual steps required" section listing any fields or files that need to be backfilled. The user follows the checklist.

**Pros:** simple, no new infrastructure
**Cons:** relies on the user actually doing it; easy to skip; upgrade.sh author must remember to add the note

### 2. Per-version migration scripts (medium effort)

`.kernel/migrations/v1.2.0.sh` — a shell script that knows how to patch existing files for that version. upgrade.sh runs any migration scripts newer than the installed version automatically.

**Pros:** automated, reliable, composable across versions
**Cons:** more infrastructure to maintain; migrations must be idempotent; needs a mechanism to track which migrations have run

### 3. upgrade.sh patches known fields with a prompt (medium effort)

upgrade.sh scans existing `sows/*/sow.config.yaml` files, detects missing fields from the template, and asks: "sow3/sow.config.yaml is missing `sow_lead` — enter a value or press enter to skip." Writes the value if provided.

**Pros:** interactive, no separate migration files, catches all existing SOWs automatically
**Cons:** makes upgrade.sh more complex; field prompts need to be maintained alongside the template

## Recommendation

Start with option 1 (migration checklist) — low effort and good enough for a small number of repos. Graduate to option 2 (migration scripts) once there are enough downstream repos that manual steps become a real pain.

## Test Plan

- upgrade.sh prints a migration checklist section when the version being upgraded introduces fields that require backfill
- Checklist correctly identifies which `sows/*/sow.config.yaml` files are missing the new field
- Running upgrade.sh a second time does not re-print the checklist if already applied
