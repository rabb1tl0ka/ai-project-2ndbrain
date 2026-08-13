# {{SOW_NAME}} — SOW Context

## Session Start

Before doing anything else for this SOW:
1. Read `sow-context.md` — current scope, status, open items, and blockers for this SOW
2. Read every file under `tasks/*.md` (excluding `tasks/done/`) — get full situational awareness of open items
3. Note any blocked tasks — these surface in TLUs as CTAs

## Task Board Rules

**Open tasks**: `sows/{{SOW_NAME}}/tasks/<task-id>.md` — one file per task
**Closed tasks**: `sows/{{SOW_NAME}}/tasks/done/<task-id>.md` — same file, moved here on close

### Surfacing tasks
When a meeting summary, working session, or conversation produces a clear action item with an owner — create a new file under `tasks/` immediately. Don't wait to be asked.

- `id`: short slug (`kickoff-01`, `arch-review-02`)
- Infer `priority` from context if the user didn't set it (`high` / `medium` / `low`)
- Leave `due` empty if unknown — don't prompt
- Set `session` to the working session slug it came from (e.g. `kickoff`, `tech-research`)
- Body: free-text description, plus a running `## Notes` log for context, blockers, links, and status-change history over the task's life

### Closing tasks
When a task is confirmed done (by the user or implied by context):
1. Add a `closed: YYYY-MM-DD` field to the file's frontmatter
2. Move the file from `tasks/<task-id>.md` to `tasks/done/<task-id>.md`

### TLU generation
- Files under `tasks/done/` with a `closed:` date in the reporting week are the primary source for "what shipped this week"
- Tasks with `status: blocked` always appear in the TLU as CTAs with owner and due date

## Task Schema

Frontmatter on every task file:

```yaml
---
id: kickoff-01
task: "Confirm data access with client IT"
owner: rommel
priority: high
due: 2026-08-20
session: kickoff
status: open
---
```

- `id`: short slug (`kickoff-01`, `arch-review-02`)
- `owner`: anyone — Loka team or client side
- `priority`: `high` / `medium` / `low`
- `due`: date or empty
- `session`: working session slug
- `status`: `open` / `blocked` (closed tasks live in `tasks/done/` instead of a `closed` status value)
- `closed`: date, added only once the file moves to `tasks/done/`

Body holds free-text description plus a `## Notes` section for context, blockers, and a running resolution log.
