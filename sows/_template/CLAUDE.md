# {{SOW_NAME}} — SOW Context

## Session Start

Before doing anything else for this SOW:
1. Read `sow-context.md` — current scope, status, open items, and blockers for this SOW
2. Read `{{SOW_NAME}}-tasks.md` — get full situational awareness of open items
3. Note any blocked tasks — these surface in TLUs as CTAs

## Task Board Rules

**File**: `sows/{{SOW_NAME}}/{{SOW_NAME}}-tasks.md`
**Done log**: `sows/{{SOW_NAME}}/done/YYYY-WW.md` (one file per ISO week)

### Surfacing tasks
When a meeting summary, working session, or conversation produces a clear action item with an owner — add it to `{{SOW_NAME}}-tasks.md` immediately. Don't wait to be asked.

- Infer `priority` from context if the user didn't set it (`high` / `medium` / `low`)
- Leave `due` empty if unknown — don't prompt
- Set `session` to the working session slug it came from (e.g. `kickoff`, `tech-research`)

### Closing tasks
When a task is confirmed done (by the user or implied by context):
1. Append it to `done/YYYY-WW.md` (current ISO week) with a `Closed` date column
2. Remove it from `{{SOW_NAME}}-tasks.md`

### TLU generation
- Read `done/YYYY-WW.md` as the primary source for "what shipped this week"
- Tasks with `status: blocked` always appear in the TLU as CTAs with owner and due date

## Task Schema

| ID | Task | Owner | Priority | Due | Session | Status | Notes |
|----|------|-------|----------|-----|---------|--------|-------|

- `ID`: short slug (`kickoff-01`, `arch-review-02`)
- `Owner`: anyone — Loka team or client side
- `Priority`: `high` / `medium` / `low`
- `Due`: date or empty
- `Session`: working session slug
- `Status`: `open` / `blocked`
- `Notes`: context, blockers, links
