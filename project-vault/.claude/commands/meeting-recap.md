Process Gemini meeting notes from Google Drive into structured meeting summaries for this project.

## Guard: check for un-replaced placeholders

Before doing anything else, check whether the configuration values below still contain `{{` and `}}`.

If either `{{GEMINI_NOTES_FOLDER}}` or `{{PROJECT_NAME}}` appears verbatim in this file (i.e. setup hasn't run yet), stop immediately and tell the user:

> "This command isn't configured yet. Run `./setup.sh` from the repo root first, then try again."

Do not proceed past this point if placeholders are detected.

## Configuration

- **Drive folder**: {{GEMINI_NOTES_FOLDER}}
- **Project filter**: {{PROJECT_NAME}}
- **State file**: `.meeting-recap-state.md` (in the vault root)
- **Summary template**: `templates/meeting-summary.md`

## Gemini filename convention

`{meeting title} - {YYYY/MM/DD HH:MM TZ} - Notes by Gemini`

Example: `CS GCP Cost Optimization - 2026/05/28 14:22 WEST - Notes by Gemini`

---

## Modes

### Default — `/meeting-recap`

1. Read `.meeting-recap-state.md` for `last_ran`. If missing or empty, default to 7 days ago.
2. Extract the Drive folder ID from the configured URL (last path segment after `/folders/`).
3. Search the folder for files whose names contain "{{PROJECT_NAME}}" and were modified after `last_ran`.
4. Process each match (see **Processing** below).
5. Report: "Processed N meetings. Found M other meetings in that period that didn't match '{{PROJECT_NAME}}' — use `--keywords` to check them."
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
   - Infer from context if obvious (e.g. meeting title matches a known SOW topic)
   - Ask the user if ambiguous

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
