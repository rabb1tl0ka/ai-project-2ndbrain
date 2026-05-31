Bootstrap this project brain from real project data: SOW documents, meeting notes, and Slack history.

## Modes

### `/bootstrap`
Process all SOW directories that have a `sow.config.yaml`. Run once after `/onboard` to load the full engagement history.

### `/bootstrap --sow <name>`
Target a single SOW by name (e.g. `/bootstrap --sow sow3`).
- If the SOW directory already exists: reprocess it only (skip all other SOWs).
- If the SOW directory does NOT exist: create it, collect its config interactively, then process it.

Use this to add a new SOW to an already-bootstrapped brain, or to refresh a single SOW without reprocessing everything.

---

## Pre-flight

1. Read `../project.config.yaml`. Extract `PROJECT_NAME`. If it's still the literal string `{{PROJECT_NAME}}` or the file doesn't exist, stop:
   > "Onboarding hasn't been run yet. Run `/onboard` from the repo root first, then come back."

2. **If `--sow <name>` was passed:**
   - If `sows/<name>/` does NOT exist: run the **New SOW setup** flow below, then jump straight to processing that SOW.
   - If `sows/<name>/` exists: skip to **For each SOW**, processing only `<name>`.

3. **If no `--sow` flag:** discover all SOW directories in `sows/` excluding `_template`.
   If none found, stop:
   > "No SOWs found. Run `/onboard` to set them up first, or run `/bootstrap --sow <name>` to add one now."
   Read `.bootstrap-state.md`. If `last_ran` has a date, warn:
   > "Bootstrap was already run on [date]. Re-running will reprocess all SOWs. Continue? [y/N]"
   Stop if declined.

---

## New SOW setup (only when `--sow <name>` targets a non-existent SOW)

1. Create the SOW directory from the template:
   ```bash
   cp -r sows/_template sows/<name>
   mv sows/<name>/sow-reference.md sows/<name>/<name>-reference.md
   ```

2. Ask for per-SOW config (press enter to skip optional fields):

   - **DRIVE_FOLDER** — "Google Drive folder URL for <name> meeting notes. Paste the URL. (Press enter to skip and fill in later.)"
   - **SOW_DOC_URL** — "Direct link to the SOW document for <name> in Google Drive. (Press enter to skip — I'll search DRIVE_FOLDER automatically.)"
   - **SLACK_CHANNELS** — "Slack channel(s) for <name>, comma-separated with # prefix. (Press enter to skip.)"
   - **GEMINI_NOTES_DOCS** — "Specific Gemini note doc URLs for <name>, comma-separated. Only needed if notes aren't all in one folder. (Press enter to skip.)"

3. Write `sows/<name>/sow.config.yaml`:
   ```yaml
   # SOW Configuration — <name>
   # Created by /bootstrap --sow <name>

   DRIVE_FOLDER: "<value or empty>"
   SOW_DOC_URL: "<value or empty>"
   SLACK_CHANNELS: "<value or empty>"
   GEMINI_NOTES_DOCS: "<value or empty>"
   ```

4. Confirm: "Created sows/<name>/. Now bootstrapping it..."

---

## For each SOW

Process every discovered SOW in order. For each `<sow>`:

### A — Read SOW config

Read `sows/<sow>/sow.config.yaml`. Extract:
- `DRIVE_FOLDER`
- `SOW_DOC_URL`
- `SLACK_CHANNELS`
- `GEMINI_NOTES_DOCS`

If the file doesn't exist or all fields are empty, warn and skip this SOW:
> "⚠ sows/<sow>/sow.config.yaml is missing or empty. Run `/onboard` to configure it, then re-run /bootstrap."

---

### B — SOW document

The SOW is the source of truth for what Loka is contractually obliged to deliver. **Bootstrap will not stop if it's missing — it will flag a warning and continue.**

**Find the SOW doc:**

1. If `SOW_DOC_URL` is a real URL (not empty), read it directly via Google Drive MCP.

2. Otherwise, search `DRIVE_FOLDER` for files whose names contain any of:
   - "SOW"
   - "Scope of Work"
   - "Implementation Proposal"

   Rules:
   - Exclude files with "Template" in the name.
   - Prefer files that also contain `PROJECT_NAME`. If still ambiguous, list candidates and ask which to use.

3. If nothing is found, ask:
   > "I couldn't find the SOW document for [sow]. You can:
   > (a) Paste a Google Drive link to it
   > (b) This SOW has no formal document — skip and continue
   > (c) Skip for now — I'll flag this as an open gap"

   - Option (a): read the doc and continue.
   - Option (b): note as intentional, no gap flagged.
   - Option (c): record `sow_missing: true`, flag in context snapshot.

**Extract from the SOW doc:**
- **Engagement scope**: what Loka is being paid to do
- **Deliverables**: explicit outputs with due dates or milestones
- **Timeline**: start/end dates, phases, key checkpoints
- **Client contacts**: people named on the client side
- **Loka team**: Loka people named in the document
- **Out-of-scope items**: anything explicitly excluded
- **Payment terms or milestone triggers**: if present

**Populate `sows/<sow>/<sow>-reference.md`:**
If it still has template placeholders, replace with extracted content. If it already has real content, append a `## From the SOW Document` section with the extracted details.

---

### C — Meeting notes

**Find the meetings:**

Priority order:

1. `DRIVE_FOLDER` is set: extract the folder ID (last segment after `/folders/`), search for ALL files whose names contain `PROJECT_NAME` — no date filter, full historical sweep.

2. `DRIVE_FOLDER` is empty but `GEMINI_NOTES_DOCS` is set: parse as comma-separated doc URLs, extract each doc ID (segment after `/d/`, before `/edit` or `?`).

3. Both empty: ask:
   > "No Drive source configured for [sow]. Paste either:
   > (a) a Google Drive folder URL, or
   > (b) individual doc URLs separated by commas
   > Press enter to skip this SOW's meetings."

If no meetings found, note it and continue.

**Process each Gemini note:**

1. Read via Google Drive MCP.
2. Extract:

   | Field | Source in the Gemini note |
   |---|---|
   | `attendees` | "Invited" list at the top |
   | `date` | Date from filename (`YYYY/MM/DD`) |
   | `type` | Internal if all @loka.com; client if any external attendees |
   | **Key Takeaways** | Narrative paragraphs in "Summary" |
   | **Decisions Made** | Bullets under "Decisions > ALIGNED" |
   | **Action Items** | "Next steps" — owner from `[Name]` prefix, due date if stated |
   | **Open Items** | Bullets under "Decisions > NEEDS FURTHER DISCUSSION" |

3. Build slug from meeting title: lowercase, kebab-case.
4. Save to `sows/<sow>/meeting-summaries/YYYY-MM-DD-<slug>.md` using `templates/meeting-summary.md`.
5. Collect all non-@loka.com attendees for the stakeholder step.

After processing this SOW's meetings: report "Processed N meetings for [sow]."

---

### D — Slack context

For each channel in `SLACK_CHANNELS` (comma-separated, strip `#` prefix):

1. Search for messages going back 90 days, or as far back as available.
2. Read threads with significant discussion (3+ replies or high reaction count).
3. Note: key decisions, blockers, recurring themes, active people.

If a channel can't be accessed, note it and continue.

Synthesize into `sows/<sow>/slack-context.md`:

```markdown
---
last_updated: YYYY-MM-DD
channels: <SLACK_CHANNELS value>
---

# Slack Context — <sow>

## Summary
(2-3 sentences: current focus, project health, visible tensions)

## Key Themes
-

## Decisions / Agreements
-

## Open Items / Blockers
-

## Active People
| Name | Slack handle | What they're focused on |
|------|-------------|------------------------|
```

If no Slack channels are configured, skip and note it.

---

## After all SOWs — Stakeholder stubs

Collect all non-@loka.com people identified across all SOWs (meeting attendees + Slack participants).

For each person:
1. Derive a name slug: lowercase-kebab of full name.
2. Check if `stakeholders/<slug>/profile.md` already exists. Skip if yes.
3. Create `stakeholders/<slug>/profile.md`:

```markdown
---
created: YYYY-MM-DD
source: bootstrap
---

# [Full Name]

**Email**: [from meeting notes, if known]
**Company**: [infer from email domain or context]
**Role**: [infer from context — leave blank if unknown]
**Slack handle**: [if seen in Slack]

## Notes
First seen: [meeting title or Slack channel, date, SOW]

## Communication style
(fill in after more interactions)

## What they care about
(fill in after more interactions)
```

Report: "Created N stakeholder stubs: [names]."

---

## After all SOWs — Context snapshot

Synthesize everything across all SOWs into `notes/project-context.md`.

The "Tensions and gaps" section is the most important output — scope creep, unaddressed commitments, and misaligned expectations. Be explicit. If nothing found: "No tensions or gaps detected at bootstrap time."

```markdown
---
last_updated: YYYY-MM-DD
generated_by: /bootstrap
sows_processed: [list]
---

# Project Context — PROJECT_NAME

## What this engagement is
(1-2 sentences from SOW docs + meetings + Slack — what is Loka actually doing?)

## SOW summary
| SOW | Scope | Status | Key dates |
|-----|-------|--------|-----------|

## Current status
(based on most recent meetings and Slack across all SOWs)

## Key people
| Name | Company | Role | SOWs |
|------|---------|------|------|

## Open items and blockers
(from meeting action items + Slack, across all SOWs)

## Key decisions made so far
(from meeting summaries, across all SOWs)

## ⚠ Tensions and gaps
Check for across all SOWs:
- **Scope creep**: work discussed or done that isn't in any SOW
- **Unaddressed commitments**: SOW deliverables with no meeting or Slack discussion yet
- **Timeline drift**: dates in SOW docs vs. pace visible in meetings/Slack
- **Missing people**: client contacts named in SOW docs who haven't appeared in meetings or Slack
- **Ambiguous ownership**: deliverables with no clear Loka owner
```

---

## Wrap up

1. Update `.meeting-recap-state.md` `last_ran` to today — future `/meeting-recap` runs only pick up new meetings.

2. Update `.bootstrap-state.md`:

```
last_ran: YYYY-MM-DD
sows_processed: <comma-separated list>
```

3. Print:

```
Bootstrap complete.

<for each SOW>
✓  [sow] SOW doc       → sows/<sow>/<sow>-reference.md
✓  [sow] N meetings    → sows/<sow>/meeting-summaries/
✓  [sow] Slack context → sows/<sow>/slack-context.md

✓  M stakeholder stubs → stakeholders/
✓  Context snapshot    → notes/project-context.md

Start here: notes/project-context.md
```

Flag any SOWs that were skipped or had missing data.
