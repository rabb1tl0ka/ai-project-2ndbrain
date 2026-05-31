Bootstrap this project brain from real project data: the SOW, meeting notes, and Slack history.

Run once after `/onboard` — it loads the vault with structured context so Claude understands the engagement from day one.

## Configuration

- **Project name**: {{PROJECT_NAME}}
- **SOW doc URL**: {{SOW_DOC_URL}}
- **Drive folder** (meeting notes): {{GEMINI_NOTES_FOLDER}}
- **Drive docs** (fallback): {{GEMINI_NOTES_DOCS}}
- **Slack channels**: {{SLACK_CHANNELS}}
- **State file**: `.bootstrap-state.md` (vault root)

---

## Pre-flight

1. Check if `{{PROJECT_NAME}}` is still the literal string `{{PROJECT_NAME}}`. If so, stop:
   > "Onboarding hasn't been run yet. Run `/onboard` from the repo root first, then come back."

2. Read `.bootstrap-state.md`. If `last_ran` has a date, warn:
   > "Bootstrap was already run on [date]. Re-running will reprocess all meetings and refresh Slack context. Continue? [y/N]"
   Stop if declined.

---

## Step 1 — SOW document

The SOW is the source of truth for what Loka is contractually obliged to deliver. Process it first — it anchors everything else.

**The SOW is optional. Bootstrap will not stop if it's missing — it will flag a warning and continue.**

**Find the SOW:**

1. If `{{SOW_DOC_URL}}` is a real URL (not the literal `{{SOW_DOC_URL}}` and not empty), read that doc directly via Google Drive MCP.

2. Otherwise, search the configured Drive folder for files whose names contain any of:
   - "SOW"
   - "Scope of Work"
   - "Implementation Proposal"

   Rules:
   - Exclude any file with "Template" in the name.
   - If multiple candidates are found, prefer files that also contain "{{PROJECT_NAME}}". If still ambiguous, list them and ask the user which one to use.

3. If nothing is found, ask:
   > "I couldn't find the SOW document. You can:
   > (a) Paste a Google Drive link to it
   > (b) This project has no SOW — skip and continue
   > (c) Skip for now — I'll flag this as an open gap"

   - Option (a): read the doc and continue.
   - Option (b): note it as intentional, skip the SOW section of the context snapshot, and continue without flagging a gap.
   - Option (c): record `sow_missing: true` and continue — the context snapshot will flag this as an open gap.

**Extract from the SOW:**

Read the full document and pull out:
- **Engagement scope**: what Loka is being paid to do
- **Deliverables**: explicit outputs — list them with any due dates or milestones stated
- **Timeline**: start/end dates, phases, key checkpoints
- **Client contacts**: people named on the client side
- **Loka team**: Loka people named in the document
- **Out-of-scope items**: anything explicitly excluded
- **Payment terms or milestone triggers**: if present

**Populate the SOW reference file:**

Find `sows/<sow-dir>/<sow-dir>-reference.md` — use the first (and likely only) SOW directory that exists, excluding `_template`. If it still has template placeholders, replace them with the extracted content. If it already has real content, append a `## From the SOW Document` section with the extracted details.

---

## Step 2 — Meeting notes

**Find the meetings:**

Priority order:

1. **Drive folder configured** — `{{GEMINI_NOTES_FOLDER}}` is a real URL (not the literal placeholder):
   - Extract the folder ID: last path segment after `/folders/`
   - Search for ALL files whose names contain "{{PROJECT_NAME}}" (no date filter — this is a full historical sweep)

2. **Specific docs configured** — `{{GEMINI_NOTES_FOLDER}}` is a placeholder or empty, but `{{GEMINI_NOTES_DOCS}}` is set and non-empty:
   - Parse as comma-separated list of doc URLs
   - Extract each doc ID: last segment after `/d/` (before any `/edit` or `?`)

3. **Nothing configured** — ask:
   > "I need the Gemini meeting notes. Paste either:
   > (a) a Google Drive folder URL containing them, or
   > (b) individual doc URLs separated by commas"
   Use the response to proceed as option 1 or 2.

If no meetings are found after searching, note it and continue — not all projects have meeting history at bootstrap time.

**Process each Gemini note:**

For each file:

1. Read it via Google Drive MCP.
2. Extract:

   | Field | Source in the Gemini note |
   |---|---|
   | `attendees` | "Invited" list at the top |
   | `date` | Date from filename (`YYYY/MM/DD`) |
   | `type` | Internal if all @loka.com; client if any external attendees present |
   | **Key Takeaways** | Narrative paragraphs in the "Summary" section |
   | **Decisions Made** | Bullets under "Decisions > ALIGNED" |
   | **Action Items** | "Next steps" — owner from `[Name]` prefix, due date if stated |
   | **Open Items** | Bullets under "Decisions > NEEDS FURTHER DISCUSSION" |

3. Build the slug from the meeting title: lowercase, kebab-case (e.g. `cs-gcp-cost-optimization`).

4. Identify the SOW:
   - Infer from context if obvious (meeting title or topic maps clearly to a SOW)
   - If multiple meetings are ambiguous, batch them into a single question rather than asking per meeting:
     > "These meetings don't clearly map to a SOW — which SOW do they belong to? [list meetings + SOW options]"

5. Save to `sows/<sow>/meeting-summaries/YYYY-MM-DD-<slug>.md` using `templates/meeting-summary.md`.

6. Collect all non-@loka.com attendees for Step 4.

After all meetings are processed:
- Update `.meeting-recap-state.md` `last_ran` to today's date — this ensures future `/meeting-recap` runs only pick up new meetings and don't reprocess history.
- Report: "Processed N meetings."

---

## Step 3 — Slack context

For each channel in `{{SLACK_CHANNELS}}` (parse as comma-separated, strip `#` prefix):

1. Search for messages going back 90 days, or as far back as available.
2. Read any threads with significant discussion (3+ replies or high reaction count).
3. Note:
   - Key decisions or agreements reached
   - Blockers and unresolved questions
   - Recurring themes or areas of tension
   - Who's most active and what they're focused on
   - Any client-side people visible in the channel

If a channel can't be accessed or doesn't exist, note it and continue.

Synthesize into `notes/slack-context.md`:

```markdown
---
last_updated: YYYY-MM-DD
channels: {{SLACK_CHANNELS}}
---

# Slack Context — {{PROJECT_NAME}}

## Summary
(2-3 sentences: what's the current focus, general project health, any visible tensions)

## Key Themes
- ...

## Decisions / Agreements
- ...

## Open Items / Blockers
- ...

## Active People
| Name | Slack handle | What they're focused on |
|------|-------------|------------------------|
```

---

## Step 4 — Stakeholder stubs

Collect all non-@loka.com people identified in Steps 2 and 3:
- Meeting attendees whose email is NOT @loka.com
- Client-side people visible in Slack

For each person:
1. Derive a name slug: lowercase-kebab of their full name (e.g. `jane-smith`).
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
First seen: [meeting title or Slack channel, date]

## Communication style
(fill in after more interactions)

## What they care about
(fill in after more interactions)
```

Report: "Created N stakeholder stubs: [names]. Fill in details as you learn more."

---

## Step 5 — Context snapshot

Synthesize everything into `notes/project-context.md`. This is the ground-truth state of the engagement as of today.

The "Tensions and gaps" section is the most important output of bootstrap — it's where scope creep, unaddressed commitments, and misaligned expectations surface. Be explicit here. If nothing was found, say so directly: "No tensions or gaps detected at bootstrap time."

```markdown
---
last_updated: YYYY-MM-DD
generated_by: /bootstrap
---

# Project Context — {{PROJECT_NAME}}

## What this engagement is
(1-2 sentences distilled from the SOW + meeting notes + Slack — what is Loka actually doing here?)

## Current status
(as of today, based on the most recent meetings and Slack activity)

## Key people
| Name | Company | Role |
|------|---------|------|

## What the SOW says Loka must deliver
(bullet list of committed deliverables, with dates if stated)

## Open items and blockers
(pulled from meeting action items + Slack open questions)

## Key decisions made so far
(pulled from meeting summaries)

## ⚠ Tensions and gaps
Contradictions between the SOW and what's visible in meetings and Slack. Check for:
- **Scope creep**: work being discussed or done that isn't in the SOW
- **Unaddressed commitments**: deliverables in the SOW with no discussion in meetings or Slack yet
- **Timeline drift**: dates in the SOW vs. pace visible in meetings/Slack
- **Missing people**: client contacts named in the SOW who haven't appeared in any meeting or Slack channel
- **Ambiguous ownership**: deliverables in the SOW where it's unclear who on Loka's side is responsible
```

---

## Step 6 — Wrap up

1. Update `.bootstrap-state.md`:

```
last_ran: YYYY-MM-DD
meetings_processed: N
slack_channels: {{SLACK_CHANNELS}}
sow_processed: true/false
```

2. Print the summary:

```
Bootstrap complete.

✓  SOW processed        → sows/<sow>/<sow>-reference.md
✓  N meetings loaded    → sows/<sow>/meeting-summaries/
✓  Slack context        → notes/slack-context.md
✓  M stakeholder stubs  → stakeholders/
✓  Context snapshot     → notes/project-context.md

Start here: notes/project-context.md
```

If the SOW was missing, flag it at the end:

```
⚠  SOW not found. Add the doc URL to project.config.yaml (SOW_DOC_URL) and re-run /bootstrap,
   or paste a link in this session and I'll process it now.
```
