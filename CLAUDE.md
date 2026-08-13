# {{CLIENT_NAME}} — Engagement Brain

## Setup (read this first)

This is an AI-powered engagement brain for a Loka client project. It's built around how Loka engagements actually run: SOWs, working sessions, stakeholders, TLUs, and a roadmap.

**If this brain hasn't been set up yet**, run `/onboard` — it collects client name, owner info, and SOW list, then replaces placeholders and creates your SOW directories.

**If onboarding is done but bootstrap hasn't run**, run `/bootstrap` — it pulls SOW docs, meeting notes, Slack history, and Notion context into the vault.

**Key files:**

| File | Purpose |
|------|---------|
| `README.md` | Full setup instructions |
| `config.example.yaml` | Config reference (3 fields) |
| `config.yaml` | Your engagement config — gitignored, never committed |
| `.claude/commands/onboard.md` | `/onboard` — guided setup |
| `.claude/commands/bootstrap.md` | `/bootstrap` — load data into the brain |

**Common questions:**
- **"What's `.kernel/`?"** — Internal repo tooling for the template maintainer. Contains the template's own roadmap (`.kernel/roadmap/`) for improvements to the brain itself — not the client engagement. Ignore it unless you're Bruno working on the template.
- **"Do I need Obsidian?"** — No. Any markdown editor works. Obsidian is recommended.
- **"I'm not a TPM — is this for me?"** — Yes. The structure instills TPM habits without requiring TPM experience.

---

## Session Start

Run `git pull` before starting any session to make sure you're on the latest version.

If this is the very first session and the vault hasn't been loaded yet, run `/bootstrap` — it pulls the SOW, meeting notes, and Slack history into the vault so Claude has real project context from the start.

Read `stakeholders/client-context.md` for the engagement-wide view. For each SOW being worked on this session, read `sows/<sow>/sow-context.md` for current status and open items. `sows/<sow>/CLAUDE.md` loads automatically — it has task board rules and session start instructions.

## Collaboration Model

This repo may have multiple contributors (e.g. two TPMs, each owning a different SOW). Main is protected — direct pushes are rejected by GitHub.

**Recommended pattern: long-lived SOW branch per PM**

Each PM owns a persistent branch tied to their SOW (e.g. `sow2-alice`). On that branch they commit and push freely — no PRs, no approvals, no friction. Periodically (end of week, before a TLU, at a milestone) they open a PR from their SOW branch into main, the other PM approves in seconds, and it merges. Everyone pulls main to get each other's updates.

- **Daily**: commit and push freely to your SOW branch
- **Periodically**: PR from `<sow>-<name>` → main, lightweight approval, merge, pull

To keep merges easy, pull main into the SOW branch regularly using merge — never rebase:
```bash
git checkout sow3
git merge origin/main
git push
```
Rebase replays commits and causes conflicts when the same changes already landed in main via a different branch. Merge just fast-forwards. The longer the branch drifts from main, the harder the eventual PR.

**For one-off changes** (not tied to a specific SOW): use a short-lived branch, open a PR when ready, merge and delete.

**If a `git push` to main fails with a GitHub branch protection error**, that's expected. Tell the user:
> "Main is protected on this repo. Let me set up your SOW branch instead."
Then:
1. Create their SOW branch: `git checkout -b <sow>-<name>` (e.g. `sow2-alice`)
2. Push it: `git push -u origin <sow>-<name>`
3. Explain they work here freely and open a PR to main when ready

**Variant: multiple contributors on the same SOW (per-person branch → SOW integration branch → main)**

Some SOWs have more than one person working on them at once (e.g. several non-technical team members contributing meeting notes, task updates, working sessions on the same SOW). In that case, the SOW branch itself becomes an integration branch rather than a single person's working branch, and each contributor gets their own branch off it:

- Naming: `<sow>-<name>` (e.g. `sow2-alice`, `sow2-beatriz`, `sow2-carla`) — a slash (`<sow>/<name>`) can't be used here: git can't have a branch named `<sow>` and a branch named `<sow>/<anything>` at the same time, since branch refs are stored in a path-like tree and `<sow>` can't be both a leaf and a directory.
- Each person commits and pushes freely to their own branch — no PRs, no friction, and they never need to touch git directly; they just ask Claude to "commit and push."
- When someone wants their work merged in, they (via Claude) open a PR from their branch into the SOW integration branch (`<sow>`), not into `main`.
- The SOW owner reviews and merges that PR into `<sow>`.
- Periodically (roughly weekly), the SOW owner opens a PR from `<sow>` into `main` — same lightweight-review ritual as the single-PM pattern above.

Before committing on behalf of a user in this setup, Claude must confirm which branch it's on and whose branch it should be:
- Run `git branch --show-current`. If it's `main`, the SOW integration branch (e.g. `<sow>`), or clearly someone else's branch, stop and ask before committing — never assume it's safe to commit to a shared or another person's branch.
- If the user hasn't identified themselves yet this session, resolve that first (see "Who are you?" below) — their name determines which per-person branch to check out or create.
- If their branch (`<sow>-<name>`) doesn't exist yet, create it off the current SOW integration branch and push it, same as the single-PM setup above.
- When they ask to "merge into `<sow>`" or similar, that means: open a PR from their personal branch into the SOW integration branch — Claude should use `gh pr create` with the base branch set explicitly, not assume `main`.

**Why this model:** SOW directories are non-overlapping so merge conflicts are rare. PRs to main are not code reviews — they're lightweight async status updates. The diff is markdown: meeting summaries, TLU drafts, stakeholder notes. It tells a story. The other lead sees exactly who you met with, what's blocked, what the client is worried about — without a single Slack message or sync meeting.

Treat the weekly PR as a ritual: open it Friday, write two sentences in the description summarizing the week. The diff does the heavy lifting. When Claude is helping you commit and push, it should suggest opening the PR to main if it's been more than a week since the last one.

**If the user is the repo owner** and gets a protection error: use a PR like anyone else, or bypass protection in GitHub settings for an emergency direct push.

---

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
**Engagement owner**: {{OWNER_NAME}} ({{OWNER_ROLE}})

---

## Vault Structure

| Directory | Purpose | Lifecycle |
|-----------|---------|-----------|
| `inbox/` | Raw captures — meeting notes, ideas, voice transcripts | Gets processed and moved out |
| `sows/` | One directory per SOW — work, meetings, deliverables | Per-SOW lifecycle |
| `stakeholders/` | Client org context (`client-context.md`) and individual stakeholder profiles | Reference |
| `team/` | Loka team member profiles | Reference |
| `notes/` | User-created notes and cross-SOW thinking | Evergreen |
| `archive/` | Processed inbox items worth keeping | Done |
| `templates/` | Working session, meeting summary, TLU templates | Reference |

---

## SOW Structure

Each SOW lives at `sows/<sow-name>/`:

| Path | Purpose |
|------|---------|
| `<sow-name>-reference.md` | What this SOW is — scope, deliverables, key dates |
| `sow-context.md` | Generated by `/bootstrap` — current scope, status, decisions, blockers for this SOW |
| `CLAUDE.md` | SOW-specific instructions auto-loaded by Claude Code when working in this directory |
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

**When the user says "generate a TLU" or "generate this week's TLU":** run `/tlu <sow>`.

**Daily TLUs** — a same-day delta report showing what's moved since the last check, meant to be run multiple times a day as a progress pulse-check. Run `/tlu-daily <sow>`. Template: `templates/tlu-daily.md`.

---

## Jira Ticket Tracking

For SOWs that need Jira-derived status in their TLUs:
- `/jira-onboard <sow>` — one-time setup: picks the Jira MCP server, project key, team roster, and JQL query, then writes `sows/<sow>/work/jira-status/CLAUDE.md`
- `/jira-overview <sow>` — refreshes a dated ticket-overview snapshot (status, days-in-status, Slack-ready Executive Summary) under `sows/<sow>/work/ticket-overview/`

`/tlu` and `/tlu-daily` check for a recent ticket-overview snapshot and ask before running `/jira-overview` themselves — it's never triggered automatically.

---

## Task Board Spreadsheet Sync

Teammates and stakeholders without repo access can get a read-only view of a SOW's task board via a Google Spreadsheet. The task files (`sows/<sow>/tasks/*.md`) are always the source of truth — the spreadsheet is a derived, one-way export.

Run `/sync-tasks` (optionally with a SOW name) to publish the current task board to Drive. Because the Google Drive MCP can't overwrite a file's content in place, **every sync creates a brand-new spreadsheet titled with today's date** rather than updating one persistent sheet. Treat this as a feature, not a workaround: each sync is a dated snapshot of task status at that moment, and older snapshots are left in Drive intentionally as history. The latest snapshot's ID and URL are written to `TASK_BOARD_SHEET_ID` / `TASK_BOARD_SHEET_URL` in `sows/<sow>/sow.config.yaml` — re-share the new link with stakeholders after each sync.

Spreadsheets are dropped into the folder set by `TASK_BOARD_FOLDER_ID` in `sow.config.yaml` — a dedicated field kept separate from `DRIVE_FOLDERS` (which is for meeting notes and often points at a client-shared folder). This should always be a Loka-internal folder. If it's empty, `/sync-tasks` will ask for a folder URL and save it before proceeding.

---

## Stakeholder & Team Profiles

**Stakeholders** (client-side): `stakeholders/<name>/profile.md`
**Team** (Loka-side): `team/<name>/profile.md`

When the user references a known stakeholder or team member by name, read their profile and use that context to tailor your answer — communication style, technical depth, concerns, what motivates them.

When logging a meeting or interaction, look up who was in the room and let their profiles inform the summary.

---

## Meeting Summaries

Meeting notes for this project are Gemini notes. Filenames follow this convention:
`{meeting title} - {YYYY/MM/DD HH:MM TZ} - Notes by Gemini`

Each SOW has its own Calendar meeting-title filter (or Drive folder) and Slack channels, configured in `sows/<sow>/sow.config.yaml`.

Use `/bootstrap` once to load all historical meetings into the vault. After that, use `/meeting-recap` for new meetings as they happen — it finds them via Calendar (matched by title) and pulls each event's attached Gemini notes, tracking which events are already processed. If this engagement predates the brain, or notes get manually copied into a shared Drive folder rather than staying attached to Calendar invites, use `/meeting-recap-drive` instead — it discovers notes by scanning a configured Drive folder.

To manually log a meeting (e.g. from a paste or a file you already have open):
1. Identify the SOW
2. Use `templates/meeting-summary.md`
3. Save to `sows/<sow-name>/meeting-summaries/YYYY-MM-DD-<slug>.md`

---

## Sprint Call Prep — Surfacing Decided vs. Open Strategic Questions

When preparing talking points for a sprint start/review call (or any prep doc ahead of a client/team call), don't just list tasks — actively audit for strategic questions that are foundational to the next stretch of work and could cause churn if left ambiguous (operating model, access model, core mechanics, output format, scope boundaries). This applies on top of whatever specific prep the user asked for, not instead of it.

For each candidate question, sort it into exactly one bucket — and require the evidence before writing the label:

- **Decided**: there's an explicit, dated moment where the team converged, quotable from a meeting summary. Restate this plainly in the prep doc so it doesn't get re-litigated — but never assume something is decided just because it's the current default or nobody objected.
- **Assumed/emergent**: it shows up as a de facto choice in an artifact (a demo, a prototype, a draft) but nobody actually decided it as a team. This is easy to mistake for "decided" because it's already reflected in the work — it isn't. Flag it as open.
- **Raised but dropped**: someone explicitly asked the question in a meeting and it was never answered. Grep for it — these are usually sitting in plain sight in a meeting summary, one line, never followed up.

Rank the open items: which ones gate the *next* work (build scope, spec decisions, pairing/assignment) go in as "force this sprint"; the rest go in as "surface for awareness, not a blocker."

Do this by actually grepping/reading meeting-summaries and sow-context — not from memory of what "seems like" it was probably decided. If the user names a specific claim (e.g. "we landed on X"), verify it against the notes and report what the evidence actually shows before building on top of it, per the global "Report what the evidence shows" instruction.

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
