Process Gemini meeting notes from Google Drive into structured meeting summaries for this project.

## Pre-flight

1. Read `../project.config.yaml` (one level up from the vault). Extract `PROJECT_NAME`. If the file doesn't exist or `PROJECT_NAME` is still the literal `{{PROJECT_NAME}}`, stop:
   > "Onboarding hasn't been run yet. Run `/onboard` from the repo root first, then try again."

2. Determine which SOW to recap meetings for:
   - Scan `sows/` for subdirectories excluding `_template`.
   - If only one SOW exists, use it.
   - If multiple SOWs exist, ask: "Which SOW are you recapping meetings for? [list options]"

3. Read `sows/<sow>/sow.config.yaml`. Extract `DRIVE_FOLDER`. If it's empty, ask:
   > "No Drive folder configured for [sow]. Paste the Google Drive folder URL for the meeting notes."

## Configuration

- **Project filter**: PROJECT_NAME (read from `../project.config.yaml`)
- **Drive folder**: DRIVE_FOLDER (read from `sows/<sow>/sow.config.yaml`)
- **State file**: `.meeting-recap-state.md` (vault root)
- **Summary template**: `templates/meeting-summary.md`

## Gemini filename convention

`{meeting title} - {YYYY/MM/DD HH:MM TZ} - Notes by Gemini`

Example: `CS GCP Cost Optimization - 2026/05/28 14:22 WEST - Notes by Gemini`

---

## Modes

### Default — `/meeting-recap`

1. Read `.meeting-recap-state.md` for `last_ran`. If missing or empty, default to 7 days ago.
2. Extract the Drive folder ID from the configured URL (last path segment after `/folders/`).
3. Search the folder for files whose names contain PROJECT_NAME and were modified after `last_ran`.
4. Process each match (see **Processing** below).
5. Report: "Processed N meetings. Found M other meetings in that period that didn't match PROJECT_NAME — use `--keywords` to check them."
6. Update `last_ran` in `.meeting-recap-state.md` to today's date.

### Keywords — `/meeting-recap --keywords {words}`

1. Read `.meeting-recap-state.md` for `last_ran`. If missing, default to 7 days ago.
2. Search the folder for files whose names contain the given keywords, modified after `last_ran`.
3. Process each match.
4. **Do NOT update `last_ran`.**

### Date — `/meeting-recap --date {date}`

1. Search the folder for all files modified on that specific date (no project name filter).
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
   | **Action Items table** | "Next steps" — owner from `[Name]` prefix, due date blank unless stated |
   | **Notes** | Bullets under "Decisions > NEEDS FURTHER DISCUSSION" flagged as open items |

3. If `--details` is passed alongside any mode, also append the "Details" section content to Notes (timestamped bullets, verbatim).

4. Identify the SOW:
   - Use the SOW identified in pre-flight if unambiguous.
   - Ask if the meeting context suggests a different SOW.

5. Build the slug from the meeting title: lowercase, kebab-case (e.g. `cs-gcp-cost-optimization`).

6. Save to `sows/<sow>/meeting-summaries/YYYY-MM-DD-<slug>.md`.

7. Flag any blockers found (items in NEEDS FURTHER DISCUSSION, or action items with no owner) as TLU material.

---

## State file format

`.meeting-recap-state.md` contains a single line:

```
last_ran: YYYY-MM-DD
```

Create it if it doesn't exist. Update `last_ran` only when the default mode completes successfully.
