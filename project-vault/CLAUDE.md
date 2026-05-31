# {{PROJECT_NAME}} — Project Brain

## Session Start

Run `git pull` before starting any session to make sure you're on the latest version.

If this is the very first session and the vault hasn't been loaded yet, run `/bootstrap` — it pulls the SOW, meeting notes, and Slack history into the vault so Claude has real project context from the start.

## Who are you?

At the start of each session, check whether the user has identified themselves (name and role). Look for this in their global `~/.claude/CLAUDE.md` or anything they've said in the current conversation.

If you don't have that information yet, ask once — briefly:

> "Before we start — who are you and what's your role on this project? (e.g. TPM, ML Lead, Tech Lead, shadowing) This helps me tailor my answers to how you actually work."

If they decline, proceed with answers useful to anyone on a project team. Never ask again.

If they identify themselves, use that context throughout the session:
- **TPM**: scope, stakeholder dynamics, deliverable status, blockers, client comms
- **ML Lead / Tech Lead**: architecture decisions, implementation depth, technical tradeoffs
- **Sales Lead**: executive frame, risks and status, no jargon
- **Shadowing**: explain the "why" behind things, not just the "what"

---

## About This Engagement

**Client**: {{CLIENT_NAME}}
**Engagement type**: {{ENGAGEMENT_TYPE}}
**Brain owner**: {{OWNER_NAME}} ({{OWNER_ROLE}}, {{OWNER_HANDLE}})

**What we're doing**: {{ENGAGEMENT_CONTEXT}}

---

## Vault Structure

| Directory | Purpose | Lifecycle |
|-----------|---------|-----------|
| `inbox/` | Raw captures — meeting notes, ideas, voice transcripts | Gets processed and moved out |
| `sows/` | One directory per SOW — work, meetings, deliverables | Per-SOW lifecycle |
| `stakeholders/` | Client stakeholder profiles | Reference |
| `team/` | Loka team member profiles | Reference |
| `roadmap/` | Challenges, ideas, and features for this engagement | Maintained by Claude |
| `notes/` | Project-level thinking and context | Evergreen |
| `archive/` | Processed inbox items worth keeping | Done |
| `templates/` | Working session, meeting summary, TLU templates | Reference |

---

## SOW Structure

Each SOW lives at `sows/<sow-name>/`:

| Path | Purpose |
|------|---------|
| `<sow-name>-reference.md` | What this SOW is — scope, deliverables, key dates |
| `work/` | Working sessions (open-ended, slug-based) |
| `meeting-summaries/` | Dated meeting notes |
| `deliverables/` | Final deliverable artifacts |

To add a new SOW: copy `sows/_template/` and rename it to the SOW name.

---

## Working Sessions

Working sessions are focused work artifacts inside a SOW. They're slug-based and open-ended — use them for any topic that needs sustained focus.

**When the user says "I need to work on [topic]" or "let's work on [topic]":**

1. Convert the topic to a kebab-case slug (e.g. "pre kickoff" → `pre-kickoff`)
2. Identify which SOW this belongs to — ask if unclear
3. Create `sows/<sow-name>/work/<slug>/`
4. Create `sows/<sow-name>/work/<slug>/<slug>.md` with this structure:

```markdown
---
status: in-progress
sow: <sow-name>
---

# <Title>

## What this is
(one sentence — what are we actually working on here)

## What I need to figure out
-

## What I already know
-

## Notes
```

5. Confirm what was created, open the file for discussion
6. Update the `## Active Working Sessions` block in the relevant SOW's reference file

When a session is done: set `status: done` in frontmatter, remove from the active sessions block. Directory stays in `work/` — do not move it.

Do NOT ask for confirmation before creating — just do it.

---

## TLUs (Traffic Light Updates)

TLUs are weekly status updates — typically for the Sales Lead or engagement sponsor. Template: `templates/tlu.md`.

**Convention:**
- Generated weekly, covering the previous week
- Output: `sows/<sow-name>/TLUs/YYYY-MM-DD-tlu.md` (date = Monday of that week)
- Status color: 🟢 Green (on track), 🟡 Yellow (at-risk items or open blockers), 🔴 Red (engagement in jeopardy)
- Audience: executive frame — risks, status, CTAs. No implementation jargon.

**When the user says "generate a TLU" or "generate this week's TLU":**
1. Read all meeting summaries, working session notes, and the SOW reference for current deliverables and blockers
2. Fill the template — achievements, blockers (with CTAs + due dates), risks (with mitigations), key notes
3. Save to the TLUs directory for that SOW

---

## Stakeholder & Team Profiles

**Stakeholders** (client-side): `stakeholders/<name>/profile.md`
**Team** (Loka-side): `team/<name>/profile.md`

When the user references a known stakeholder or team member by name, read their profile and use that context to tailor your answer — communication style, technical depth, concerns, what motivates them.

When logging a meeting or interaction, look up who was in the room and let their profiles inform the summary.

---

## Meeting Summaries

Meeting notes for this project live in Google Drive as Gemini notes. Filenames follow this convention:
`{meeting title} - {YYYY/MM/DD HH:MM TZ} - Notes by Gemini`

Each SOW has its own Drive folder and Slack channels, configured in `sows/<sow>/sow.config.yaml`.

Use `/bootstrap` once to load all historical meetings into the vault. After that, use `/meeting-recap` for new meetings as they happen — it picks up only what's changed since the last run.

To manually log a meeting (e.g. from a paste or a file you already have open):
1. Identify the SOW
2. Use `templates/meeting-summary.md`
3. Save to `sows/<sow-name>/meeting-summaries/YYYY-MM-DD-<slug>.md`

---

## Inbox Processing

When the user says "process my inbox":
1. Read each item in `inbox/`
2. Route to the right place: working session note, meeting summary, stakeholder log, roadmap idea, or `notes/`
3. Move processed items to `archive/` or their destination
4. Never delete without asking

---

## Key Behaviors (Always Active)

- **SOW-first thinking**: when the user describes work, connect it to a SOW. If it doesn't fit any active SOW, note that — it may be scope creep or a new engagement.
- **Stakeholder awareness**: when a client stakeholder is mentioned, reference their profile if it exists. Flag if a profile is missing and offer to create one.
- **Blockers surface up**: when you see a blocker in a working session or meeting note, flag it as TLU material.
- **Don't bury the lede**: if you spot a risk or a decision that needs to be made, say it plainly. Don't soften it.

---

@roadmap/CLAUDE.md
