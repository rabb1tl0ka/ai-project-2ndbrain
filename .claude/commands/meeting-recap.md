Process Gemini meeting notes for this project, discovered via Google Calendar events.

For projects that predate this brain (or where notes get manually copied into a shared Drive folder instead), use `/meeting-recap-drive` instead — see that command for when to reach for it.

## Pre-flight

1. Determine which SOW to recap meetings for:
   - Scan `sows/` for subdirectories excluding `_template`.
   - If only one SOW exists, use it.
   - If multiple SOWs exist, ask: "Which SOW are you recapping meetings for? [list options]"

2. Read `sows/<sow>/sow.config.yaml`. Extract `MEETING_TITLE_FILTER`, `CALENDAR_ID`, `LOOKBACK_DAYS`.
   - If `MEETING_TITLE_FILTER` is missing, but the old single-value `MEETING_FILTER` field is set, treat it as a one-item list — don't error or ask the user to migrate it.
   - If neither is set, ask: "What string(s) should I match in Google Calendar event titles to find [sow]'s meetings? (comma-separated if more than one, e.g. 'AI Design Cards Digital, Design Sprint')" — split on commas, trim whitespace, write as a list under `MEETING_TITLE_FILTER` in `sow.config.yaml`.

## Configuration

- **Title filter**: `MEETING_TITLE_FILTER` — list of strings, OR logic, case-insensitive substring match against the event title. An event matches if its title contains **any** entry.
- **Calendar**: `CALENDAR_ID` (optional, defaults to `primary`)
- **Lookback window**: `LOOKBACK_DAYS` (optional, defaults to 14) — bounds the Calendar search each run. It exists purely to bound the query, not to dedupe — that's the state file's job.
- **State file**: `sows/<sow>/.meeting-recap-state.md`
- **Summary template**: `templates/meeting-summary.md`

### State file — per-event tracking, not a date cursor

A date cursor can't handle multiple same-day meetings where some are already processed and others aren't. `sows/<sow>/.meeting-recap-state.md` tracks **which specific calendar events have been handled**:

```markdown
## Processed events
- id: 1vq77pagc28rqs1te3s9n7e2f4
  date: 2026-07-26
  title: "AI Design Cards Digital - Weekly Sprint Start/Review"
  status: done
- id: abc123xyz
  date: 2026-07-24
  title: "AI Design Cards Digital - Kickoff"
  status: skipped
```

- `status: done` — meeting summary already saved for this event, never reprocess it.
- `status: skipped` — Gemini notes weren't ready last time this event was checked; retry it.
- Create the file (empty `## Processed events` list) if missing. If an old `last_ran: YYYY-MM-DD` file exists from a previous version of this skill, treat it as an empty processed-events list — don't error, don't try to migrate it, just start tracking events fresh from here.
- Events stay in the list indefinitely (bounded naturally by `LOOKBACK_DAYS` — an event that ages out of the search window stops being re-checked anyway, so the list doesn't need separate pruning).

## Gemini filename convention

`{meeting title} - {YYYY/MM/DD HH:MM TZ} - Notes by Gemini`

Example: `CS GCP Cost Optimization - 2026/05/28 14:22 WEST - Notes by Gemini`

---

## Modes

### Default — `/meeting-recap`

1. Read the processed-events list from `sows/<sow>/.meeting-recap-state.md`.
2. Search Google Calendar (`CALENDAR_ID`) for events whose title contains any entry in `MEETING_TITLE_FILTER`, within the last `LOOKBACK_DAYS` days up to now.
3. For each matching event, check it against the processed-events list:
   - `status: done` → already handled, skip silently.
   - `status: skipped` or not in the list at all (new event) → attempt to process it this run.
4. If nothing needs attempting, report that and stop.
5. Process each event that needs attempting (see **Processing** below). An event whose Gemini doc isn't attached yet (notes not ready) is **skipped, not an error** — note its date and move on.
6. After each event, upsert its record in the processed-events list: `status: done` on success, `status: skipped` if notes weren't ready.
7. Report: "Processed N meetings." List any skipped events (title + date) — they'll be retried automatically next run.

### `--date {date}`

1. Search Calendar for title-matching events on that exact date (ignoring `LOOKBACK_DAYS`).
2. If more than one matches, list them and ask which to process.
3. Process selected matches — this mode **does** consult and update the processed-events list, same dedup rules as default, so re-running it doesn't reprocess an event already marked `done`.

---

## Processing one event

### 1 — Locate the Gemini doc

Pull it from the calendar event's own `attachments` — find the entry titled "Notes by Gemini" and take its `fileUrl`, extracting the Drive doc ID from it. Don't derive the filename and search Drive separately; the event already carries a direct link.

If no such attachment exists yet, the notes likely aren't ready (Gemini can take a while, or the meeting wasn't transcribed) — record the event as **skipped** and continue to the next matching event.

### 2 — Read and extract

1. Read the doc via Google Drive MCP.
2. Extract the following from the Gemini structure:

   | Template field | Source in Gemini note |
   |---|---|
   | `attendees` | "Invited" list at the top |
   | `date` | Calendar event's start date |
   | `type` | Infer: internal if all @loka.com, client if external attendees |
   | **Key Takeaways** | Narrative paragraphs in the "Summary" section |
   | **Decisions Made** | Bullets under "Decisions > ALIGNED" |
   | **Actions checkboxes** | "Next steps" — one `- [ ] task (owner: name) (due: yyyy-MM-dd)` per item; owner from `[Name]` prefix, omit the `(due: ...)` tag entirely unless an exact yyyy-MM-dd date is stated |
   | **Notes** | Bullets under "Decisions > NEEDS FURTHER DISCUSSION" flagged as open items |

3. If `--details` is passed alongside any mode, also append the "Details" section content to Notes (timestamped bullets, verbatim).

4. Identify the SOW:
   - Use the SOW identified in pre-flight if unambiguous.
   - Ask if the meeting context suggests a different SOW.

5. Build the slug from the meeting title: lowercase, kebab-case (e.g. `cs-gcp-cost-optimization`).

6. Save to `sows/<sow>/meeting-summaries/YYYY-MM-DD-<slug>.md`.

7. Flag any blockers found (items in NEEDS FURTHER DISCUSSION, or action items with no owner) as TLU material.

---

## Task board review

After all meetings are processed, review the task board and propose updates based on what surfaced across the meeting summaries.

1. Read the current task board: `sows/<sow>/<sow>-tasks.md`
2. Read the current week's done log: `sows/<sow>/done/YYYY-WW.md` (current ISO week)
3. Scan all processed meeting summaries for:
   - **New action items** with a clear owner → candidate for a new task
   - **Resolved items** — tasks confirmed done by anyone in the meeting → candidate to close
   - **Status changes** — a blocker that got unblocked, or a new blocker introduced → candidate to update
   - **New blockers** from NEEDS FURTHER DISCUSSION or unowned action items → candidate to add as `blocked`

4. Present a proposed diff — do not write anything yet:

   ```
   ## Proposed task board changes

   ADD
   - [slug]: [task description] | [owner] | [priority] | [due if known] | [session slug]

   CLOSE
   - [task-id]: [reason from meeting]

   UPDATE
   - [task-id]: [what changes and why]

   No changes needed: [task-ids that appeared in the meeting but are already accurate]
   ```

5. Ask: "Apply these changes, adjust, or skip?"

6. On confirmation, apply the changes:
   - New tasks: append rows to the task board following the task schema
   - Closed tasks: move to the done log (`sows/<sow>/done/YYYY-WW.md`) with today's date, remove from task board
   - Updated tasks: edit the relevant row in place

### Task schema (for reference when adding rows)

| ID | Task | Owner | Priority | Due | Session | Status | Notes |
|----|------|-------|----------|-----|---------|--------|-------|

- `ID`: short slug (`kickoff-01`, `arch-review-02`)
- `Priority`: `high` / `medium` / `low` — infer from context if not explicit
- `Due`: date if stated, otherwise empty
- `Session`: slug of the working session this came from, or the meeting slug if no working session applies
- `Status`: `open` or `blocked`
