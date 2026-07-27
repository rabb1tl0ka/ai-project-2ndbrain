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

1. **If `--sow <name>` was passed:**
   - If `sows/<name>/` does NOT exist: run the **New SOW setup** flow below, then jump straight to processing that SOW.
   - If `sows/<name>/` exists: check whether it has already been bootstrapped by counting `.md` files in `sows/<name>/meeting-summaries/` and checking if `sows/<name>/slack-context.md` exists. If either has content, warn:
     > "sow2 looks already bootstrapped (N meeting summaries, slack context ✓). Re-running will re-fetch everything from Drive and Slack — use `/meeting-recap` (or `/meeting-recap-drive` if this SOW's notes still live in a Drive folder) instead to pick up new meetings cheaply. Re-run full bootstrap anyway? [y/N]"
     Stop if declined. Otherwise continue to **For each SOW**, processing only `<name>`.

2. **If no `--sow` flag:** discover all SOW directories in `sows/` excluding `_template`.
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

2. Ask for per-SOW config **one field at a time** — send each question as its own message and wait for the user's reply before asking the next. Do NOT list all questions at once.

   Ask in this order, one per message:
   1. **DRIVE_FOLDERS** — "Google Drive folder URL(s) for <name> meeting notes — comma-separated if you have multiple. (Press enter to skip and fill in later.)"
   2. **SOW_DOC_URL** — "Direct link to the SOW document for <name> in Google Drive. (Press enter to skip — I'll search DRIVE_FOLDERS automatically.)"
   3. **SLACK_CHANNELS** — "Slack channel(s) for <name>, comma-separated with # prefix. (Press enter to skip.)"
   4. **GEMINI_NOTES_DOCS** — "Specific Gemini note doc URLs for <name>, comma-separated. Only needed if notes aren't all in one folder. (Press enter to skip.)"

3. Write `sows/<name>/sow.config.yaml`:
   ```yaml
   # SOW Configuration — <name>
   # Created by /bootstrap --sow <name>

   DRIVE_FOLDERS: "<value or empty>"
   MEETING_FILTER: "<value or empty>"
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
- `DRIVE_FOLDERS`
- `MEETING_FILTER`
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

2. Otherwise, search each folder in `DRIVE_FOLDERS` for files whose names contain any of:
   - "SOW"
   - "Scope of Work"
   - "Implementation Proposal"

   Rules:
   - Exclude files with "Template" in the name.
   - If still ambiguous, list candidates and ask which to use.

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

1. `DRIVE_FOLDERS` is set: parse as comma-separated URLs. For each folder, extract the folder ID (last segment after `/folders/`) and list all files — no date filter, full historical sweep. Deduplicate across folders by file ID. If `MEETING_FILTER` is set, only process files whose names contain that string.

2. `DRIVE_FOLDERS` is empty but `GEMINI_NOTES_DOCS` is set: parse as comma-separated doc URLs, extract each doc ID (segment after `/d/`, before `/edit` or `?`).

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
   | **Actions checkboxes** | "Next steps" — one `- [ ] task (owner: name) (due: yyyy-MM-dd)` per item; owner from `[Name]` prefix, omit the `(due: ...)` tag entirely unless an exact yyyy-MM-dd date is stated |
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

### E — Notion channel

Read `NOTION_PROJECT_URL` from the SOW config.

If empty or not set, ask:
> "Do you have a Notion project URL for [sow]? Paste it to pull Notion context, or press enter to skip."

- If they paste a URL: write it back to `sows/<sow>/sow.config.yaml` as `NOTION_PROJECT_URL: "<url>"`, then continue.
- If they press enter: note it and skip the rest of this section.

If set:

1. **Check Notion connector.** If unavailable, print:
   > "⚠ NOTION_PROJECT_URL is set for [sow] but the Notion connector isn't available. Skipping Notion channel. Enable it in Claude settings to pull Notion context during bootstrap."

   Skip the rest of this section.

2. **Fetch child pages.** Using the Notion MCP, list all child pages of `NOTION_PROJECT_URL`.
   If none found, note it and skip.

3. **Read each child page.** For each child page, read its full content.

4. **Synthesize into `sows/<sow>/notion-context.md`:**

```markdown
---
last_updated: YYYY-MM-DD
source: <NOTION_PROJECT_URL>
---

# Notion Context — <sow>

## Summary
(2-3 sentences: what's published here, what it tells us about project status or decisions)

## Pages found
| Title | Last edited | Key content |
|-------|-------------|-------------|

## Key information extracted
-
```

---

### F — SOW context snapshot

Synthesize everything gathered for this SOW (steps B through E) into `sows/<sow>/sow-context.md`. This is the primary context file Claude reads when working inside this SOW.

```markdown
---
last_updated: YYYY-MM-DD
generated_by: /bootstrap
sow: <sow>
---

# SOW Context — <sow>

## What this SOW is
(1-2 sentences: what Loka is delivering, why the client wants it)

## Scope summary
- Key deliverables with due dates or milestones
- Out-of-scope items worth noting

## Current status
(based on most recent meetings and Slack for this SOW)

## Key people on this SOW
| Name | Company | Role |
|------|---------|------|

## Key decisions made
(from meeting summaries for this SOW)

## Open items and blockers
(from meeting action items + Slack for this SOW — flag any `status: blocked` as TLU material)

## ⚠ Tensions and gaps
- **Scope creep**: work discussed or done that isn't in this SOW
- **Unaddressed commitments**: SOW deliverables with no meeting or Slack discussion yet
- **Timeline drift**: dates in the SOW doc vs. pace visible in meetings/Slack
- **Ambiguous ownership**: deliverables with no clear Loka owner
```

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

## After all SOWs — Client context

Synthesize the client-level view across all SOWs into `stakeholders/client-context.md`. This is engagement-wide context — who the client is, the overall health of the relationship, and tensions that span SOWs. Per-SOW detail lives in each `sows/<sow>/sow-context.md`.

The "Cross-SOW tensions" section is the most important output — scope creep, unaddressed commitments, and misaligned expectations that span multiple SOWs. Be explicit. If nothing found: "No cross-SOW tensions detected at bootstrap time."

```markdown
---
last_updated: YYYY-MM-DD
generated_by: /bootstrap
sows_processed: [list]
---

# Client Context — {{CLIENT_NAME}}

## Who this client is
(1-2 sentences: what does this company do, what's their industry, why did they engage Loka)

## What Loka is doing for them
(1-2 sentences: the overall engagement mission across all SOWs)

## SOW map
| SOW | Scope summary | Status | Context file |
|-----|---------------|--------|--------------|
| sow1 | ... | ... | [sow-context.md](../sows/sow1/sow-context.md) |

## Key people across SOWs
| Name | Company | Role | SOWs |
|------|---------|------|------|

## Overall engagement health
(based on most recent meetings and Slack across all SOWs — is the relationship healthy? Any recurring friction?)

## ⚠ Cross-SOW tensions and gaps
Check across all SOWs for issues that span engagement-wide:
- **Scope creep**: work discussed or done that isn't in any SOW
- **Unaddressed commitments**: SOW deliverables with no meeting or Slack discussion yet
- **Timeline drift**: dates in SOW docs vs. pace visible in meetings/Slack
- **Missing people**: client contacts named in SOW docs who haven't appeared in meetings or Slack
- **Ambiguous ownership**: deliverables with no clear Loka owner across SOWs
```

---

## Wrap up

1. **Ensure the standard skills are available.**

   For each skill below, check whether `.claude/skills/<skill>/SKILL.md` already exists in this repo. If it does, skip that skill silently.

   - `action-board` — consolidated open-actions board across meeting summaries and working sessions
   - `github-commit` — grouped, approved commits from the working tree
   - `github-branch-publish` — commit, push, and open a PR in one shot

   Pull in whichever of these are missing from their source repo, so every contributor gets them automatically on clone, with no separate global install needed:
   ```bash
   git clone --depth 1 https://github.com/rabb1tl0ka/claude-skills.git /tmp/claude-skills-bootstrap
   mkdir -p .claude/skills
   cp -r /tmp/claude-skills-bootstrap/action-board .claude/skills/action-board          # if missing
   cp -r /tmp/claude-skills-bootstrap/github-commit .claude/skills/github-commit        # if missing
   cp -r /tmp/claude-skills-bootstrap/github-branch-publish .claude/skills/github-branch-publish  # if missing
   rm -rf /tmp/claude-skills-bootstrap
   ```
   If the clone fails (no network), note it and continue — the brain still works, these skills just won't be available until someone copies them in manually. This is a one-time step per skill; it won't re-copy a skill that's already present, so it never overwrites local edits to it.

2. **Create SOW branch(es) if missing.**

   For each SOW that was processed, check whether a remote branch exists:
   ```bash
   git ls-remote --heads origin <sow>
   ```
   If the branch doesn't exist locally or remotely, create and push it:
   ```bash
   git checkout -b <sow>
   git push -u origin <sow>
   git checkout -
   ```
   If it already exists, skip silently.

   This is the branch everyone on this SOW works from — no PRs needed for day-to-day commits. PRs only go from `<sow>` → `main`.

3. If this SOW's meetings were pulled via `DRIVE_FOLDERS`/`GEMINI_NOTES_DOCS` (this bootstrap step uses the same Drive-based discovery as `/meeting-recap-drive`), update `.meeting-recap-drive-state.md` `last_ran` to today — future `/meeting-recap-drive` runs only pick up new meetings. This doesn't seed `/meeting-recap`'s Calendar-based state — that skill tracks its own processed events independently and will pick up any Calendar-attached meetings on its own next run.

4. Update `.bootstrap-state.md`:

```
last_ran: YYYY-MM-DD
sows_processed: <comma-separated list>
```

5. Print:

```
Bootstrap complete.

✓  action-board skill   → .claude/skills/action-board/  (or "already present" / "skipped — clone failed")

<for each SOW>
✓  [sow] SOW doc        → sows/<sow>/<sow>-reference.md
✓  [sow] N meetings     → sows/<sow>/meeting-summaries/
✓  [sow] Slack context  → sows/<sow>/slack-context.md
✓  [sow] Notion context → sows/<sow>/notion-context.md  (or "skipped — not configured")
✓  [sow] SOW context    → sows/<sow>/sow-context.md
✓  [sow] branch         → origin/<sow>  (or "already existed")

✓  M stakeholder stubs  → stakeholders/
✓  Client context       → stakeholders/client-context.md

Start here: stakeholders/client-context.md
```

Flag any SOWs that were skipped or had missing data.
