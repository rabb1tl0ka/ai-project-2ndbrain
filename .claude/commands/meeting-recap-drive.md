Process Gemini meeting notes from a Google Drive folder into structured meeting summaries for this project.

Use this instead of `/meeting-recap` when meeting notes for this SOW don't reliably show up as Calendar-event attachments — most commonly because the engagement predates this brain (historical transcripts already sitting in a shared Drive folder, from before anyone was tracking Calendar events for it) or because notes get manually copied into a shared/client folder rather than staying attached to whoever's personal Calendar invite generated them. `/meeting-recap` (Calendar-first) is the default for ongoing use once the brain is set up; this one is for backfill and folder-based workflows.

## Pre-flight

1. Determine which SOW to recap meetings for:
   - Scan `sows/` for subdirectories excluding `_template`.
   - If only one SOW exists, use it.
   - If multiple SOWs exist, ask: "Which SOW are you recapping meetings for? [list options]"

2. Read `sows/<sow>/sow.config.yaml`. Extract `DRIVE_FOLDERS` and `MEETING_FILTER`. If `DRIVE_FOLDERS` is empty, ask:
   > "No Drive folder configured for [sow]. Paste one or more Google Drive folder URLs (comma-separated) for the meeting notes."

## Configuration

- **Drive folder**: DRIVE_FOLDERS (read from `sows/<sow>/sow.config.yaml`)
- **Meeting filter**: MEETING_FILTER (read from `sows/<sow>/sow.config.yaml` — optional, applied when set; filename substring match)
- **State file**: `.meeting-recap-drive-state.md` (repo root)
- **Summary template**: `templates/meeting-summary.md`

## Gemini filename convention

`{meeting title} - {YYYY/MM/DD HH:MM TZ} - Notes by Gemini`

Example: `CS GCP Cost Optimization - 2026/05/28 14:22 WEST - Notes by Gemini`

---

## Modes

### Default — `/meeting-recap-drive`

1. Read `.meeting-recap-drive-state.md` for `last_ran`. If missing or empty, default to 7 days ago.
2. Parse `DRIVE_FOLDERS` as comma-separated URLs. For each folder, extract the folder ID (last segment after `/folders/`).
3. Search each folder for files modified after `last_ran`. Deduplicate across folders by file ID. If `MEETING_FILTER` is set, only include files whose names contain that string.
4. Process each match (see **Processing** below).
5. Report: "Processed N meetings since <last_ran>." If MEETING_FILTER was applied, note it: "(filtered by '<MEETING_FILTER>')"
6. Update `last_ran` in `.meeting-recap-drive-state.md` to today's date.

### Keywords — `/meeting-recap-drive --keywords {words}`

1. Read `.meeting-recap-drive-state.md` for `last_ran`. If missing, default to 7 days ago.
2. Search the folder for files whose names contain the given keywords, modified after `last_ran`.
3. Process each match.
4. **Do NOT update `last_ran`.**

### Date — `/meeting-recap-drive --date {date}`

1. Search the folder for all files modified on that specific date.
2. Present the list and ask which ones to process.
3. Process selected matches.
4. **Do NOT update `last_ran`.**

---

## Processing a Gemini note

For each file:

1. Read the file using Google Drive MCP.
2. Extract the following from the Gemini structure:

   | Template field | Source in Gemini note |
   |---|---|
   | `attendees` | "Invited" list at the top |
   | `date` | Date from filename |
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

1. Read the current open task files: `sows/<sow>/tasks/*.md`
2. Read this week's closed task files: `sows/<sow>/tasks/done/*.md`, filtered to `closed:` dates in the current ISO week
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
   - New tasks: create `sows/<sow>/tasks/<task-id>.md` following the task schema, with the meeting/session context as the file body
   - Closed tasks: add `closed: YYYY-MM-DD` (today) to the file's frontmatter and move it to `sows/<sow>/tasks/done/<task-id>.md`
   - Updated tasks: edit the relevant file's frontmatter or `## Notes` section in place

### Task schema (for reference when creating task files)

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

- `ID`: short slug (`kickoff-01`, `arch-review-02`)
- `Priority`: `high` / `medium` / `low` — infer from context if not explicit
- `Due`: date if stated, otherwise empty
- `Session`: slug of the working session this came from, or the meeting slug if no working session applies
- `Status`: `open` or `blocked`

---

## State file format

`.meeting-recap-drive-state.md` contains a single line:

```
last_ran: YYYY-MM-DD
```

Create it if it doesn't exist. Update `last_ran` only when the default mode completes successfully.
