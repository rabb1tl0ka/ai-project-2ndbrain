# AI Project 2nd Brain

A Claude-powered engagement knowledge system for Loka projects. Create a repo from this template, configure it in 2 minutes, and have a working brain that Claude understands from day one.

Structured the way a TPM thinks — so whether you're an ML Lead, Tech Lead, or shadowing engineer, the brain helps you work like a TPM would: tracking stakeholders, organizing by SOW, running working sessions, and generating TLUs.

## What's inside

```
inbox/               ← raw captures land here first
sows/                ← one directory per SOW
  _template/         ← copy this to create a new SOW
stakeholders/        ← client stakeholder profiles
team/                ← Loka team member profiles
notes/               ← project-level thinking and context
archive/             ← processed inbox items worth keeping
templates/           ← working session, meeting summary, TLU templates
config.example.yaml  ← config reference (3 fields)
config.yaml          ← your engagement config, gitignored — never committed
```

## Setup

> **Are you the engagement owner setting this up for the first time, or a contributor joining an existing brain?**
> - **Contributor:** the brain is already bootstrapped — see [Joining an existing brain](#joining-an-existing-brain) just below
> - **Owner:** setting this up for the first time — follow [Creating a new brain](#creating-a-new-brain)

## Branching strategy

Before you touch git, know where your work actually lands. A SOW with multiple contributors uses three tiers:

```
main              ← protected, one PR + approval away from any branch
 └─ <sow>         ← SOW integration branch, owned by the SOW lead
     └─ <sow>-<yourname>   ← your own branch, freely commit/push here
     └─ <sow>-<othername>  ← another contributor's branch
```

- **`main`**: protected. Nothing merges in without a PR and an approval.
- **`<sow>`** (the SOW branch): an integration branch, not a personal one. The SOW lead reviews and merges into it. Don't commit here directly.
- **`<sow>-<yourname>`**: your own branch. Commit and push freely, no PR needed for your own work-in-progress.

The flow: you work on `<sow>-<yourname>` → open a PR into `<sow>` when ready → the SOW lead merges it → periodically the SOW lead PRs `<sow>` into `main`.

You never need to type any of this yourself — `/onboard` and `/github-branch-publish` figure out your branch name from your config and this repo's convention. See [Multi-contributor workflow](#multi-contributor-workflow) for the full model, including the simpler single-lead variant (`sow1`, `sow2`, no per-person sub-branches).

## Joining an existing brain

Someone already created and configured the repo. You just need to clone it and set up your local config.

**1. Clone the repo**
```bash
git clone https://github.com/<your-org>/<client>-ai-2ndbrain
cd <client>-ai-2ndbrain
```

**2. Run `/onboard`**

Start Claude Code from the repo root:
```bash
claude
```

Then run:
```
/onboard
```

This sets up your local `config.yaml` (name, role) and any SOW directories you're contributing to. It detects the existing engagement config and only asks for what's missing.

`config.yaml` is gitignored — it never gets committed.

**3. Orient yourself**
```
/2ndbrain
```

It reads your current state and tells you exactly what to do next — including where to read for context (`stakeholders/client-context.md`, `sows/<sow>/sow-context.md`) and which branch to work on.

**4. See what's on your plate**
```
/action-board --owner "Your Name"
```
Shows every open `- [ ]` action across the vault attributed to you — pulled from working sessions, meeting summaries, and TLUs.

**5. Ask Claude to work on a task**

Just say *"let's work on <task>"*. Claude creates a slug-based working session under the right SOW (`sows/<sow>/work/<slug>/`) and you go from there — no need to create files by hand.

**6. Save your progress**

When you're ready to check in your work:
- `/github-commit` — commits your changes, grouped by theme, with no push. Good for saving progress mid-task.
- `/github-branch-publish` — commits, pushes to your branch, and opens a PR in one shot. You don't need to name a branch or a base — Claude reads your config and this repo's [branching strategy](#branching-strategy) to figure out both (your personal branch as head, the SOW branch as base).

**7. Stay current with the rest of the team**

Other contributors are merging into your SOW branch too — pull their work into yours every so often with:
```
/github-branch-refresh
```
This merges your SOW branch's latest into whatever branch you're on and pushes straight to your own branch — no PR needed, since it's your branch. Run it before starting a new task, or any time it's been a few days since you last checked in.

See [Multi-contributor workflow](#multi-contributor-workflow) below for the full collaboration model.

---

## Creating a new brain

**1. Create a repo from this template**

On GitHub, click **Use this template → Create a new repository** (one repo per engagement). Name it `<client>-ai-2ndbrain` and set visibility to private.

Then clone your new repo:
```bash
git clone https://github.com/<your-org>/<client>-ai-2ndbrain
cd <client>-ai-2ndbrain
```

**2. Run /onboard**

Start Claude Code from the repo root:
```bash
claude
```

Then run:
```
/onboard
```

Claude asks for client name, your name and role, and which SOWs to set up. It writes `config.yaml`, replaces all `{{placeholders}}`, and creates your SOW directories. Takes about 2 minutes.

`config.yaml` is gitignored — your config is never committed.

**3. Run /bootstrap**

```
/bootstrap
```

This pulls in the SOW document, all historical meeting notes from Google Drive, and recent Slack history — then generates a context snapshot, stakeholder stubs, and a tensions/gaps report between what the SOW commits to and what's actually happening.

**4. Fill in any gaps**

Open `stakeholders/client-context.md` for the engagement-wide view, and each `sows/<sow>/sow-context.md` for per-SOW status. Fill in team profiles in `team/`, enrich stakeholder profiles in `stakeholders/`, and address any tensions flagged by bootstrap.

**5. Create your SOW branch and push**

Main is protected — don't push directly to it. Each SOW lead owns a dedicated branch:

```bash
git checkout -b sow1          # if you're the SOW lead
git checkout -b sow1-yourname # if you're a contributor to someone else's SOW
git add -A && git commit -m "init: configure engagement brain"
git push -u origin HEAD
```

See [Multi-contributor workflow](#multi-contributor-workflow) below for the full collaboration model.

**6. Orient yourself anytime**

Run `/2ndbrain` — it reads your current state and tells you exactly what to do next.

## Commands

All commands run from the repo root in a Claude Code session (`claude`).

### Setup

| Command | When to run | What it does |
|---------|------------|--------------|
| `/onboard` | Once, after forking | Collects client name, owner info, SOW list. Writes `config.yaml`, replaces placeholders, creates SOW dirs. |
| `/bootstrap` | Once per SOW, after onboard | Pulls SOW doc, meeting notes, Slack history, and Notion context into the vault. Generates stakeholder stubs and a tensions/gaps report. |
| `/bootstrap --sow <name>` | When adding a new SOW | Creates the SOW dir, collects its config, and bootstraps it. |

### Ongoing

| Command | What it does |
|---------|-------------|
| `/2ndbrain` | Orientation — shows current setup state, SOW summary, and notifies if a template update is available. |
| `/meeting-recap` | Picks up new meetings via Google Calendar (matched by title) and pulls each one's attached Gemini notes. Incremental — tracks processed events, only handles what's new. |
| `/meeting-recap --date <date>` | Fetch meetings from a specific date. |
| `/meeting-recap-drive` | Same output, but discovers Gemini notes from a Drive folder instead of Calendar. Use for backfilling engagements that predate this brain, or when notes are manually copied into a shared folder. |
| `/meeting-recap-drive --keywords <words>` | Search for specific keywords in recent meetings (Drive variant). |
| `/meeting-recap-drive --date <date>` | Fetch meetings from a specific date (Drive variant). |
| `/tlu <sow>` | Generates this week's Traffic Light Update, pulling from meeting summaries, working sessions, and (if available) the latest Jira ticket-overview snapshot. |
| `/tlu-daily <sow>` | Generates a same-day delta report — what's moved since the last check. Meant to be run multiple times a day. |
| `/action-board [path] [--all\|--overdue] [--owner <name>]` | Scans for `## Actions` checkbox sections across the vault and prints a consolidated, prioritized board of open items. Also triggers on phrases like "what's on my plate". |

### Jira

| Command | When to run | What it does |
|---------|------------|--------------|
| `/jira-onboard [sow]` | Once per SOW | Sets up Jira status tracking — picks the MCP server, project key, team roster, and JQL query, then writes `sows/<sow>/work/jira-status/CLAUDE.md`. |
| `/jira-overview [sow]` | As needed, or when `/tlu`/`/tlu-daily` ask for it | Refreshes a dated ticket-overview snapshot: status, days-in-status, what's new, and a Slack-ready Executive Summary. |

### Notion

| Command | What it does |
|---------|-------------|
| `/publish-to-notion <file>` | Publishes any vault `.md` file to Notion as a child page of the SOW's project page. Idempotent — republishing updates the existing page. |
| `/fetch-from-notion [sow]` | Pulls all child pages from the Notion project page, traverses TLU history chains, writes `notion-context.md`. |

### Git workflow

| Command | What it does |
|---------|-------------|
| `/github-commit` | Groups your working tree's changes by theme and proposes one commit per group. Never pushes — commit only, after you approve the full plan. |
| `/github-branch-publish [branch] [--base <branch>]` | Same grouped-commit flow, then pushes to a branch and opens a PR — commit to PR in one shot. Defaults to your own branch per this repo's naming convention (see [Multi-contributor workflow](#multi-contributor-workflow)) if none is given. |
| `/github-branch-refresh [main]` | Pulls the latest from your branch's parent (your SOW branch, or `main` if passed) into whatever you're on, then pushes — always to your own branch, never a PR. Run this periodically so your branch doesn't drift behind other contributors' merged work. |

### Maintenance

| Command | What it does |
|---------|-------------|
| `/upgrade` | Checks if a newer version of the template is available. |
| `/upgrade --apply` | Pulls the latest tooling from the template repo and commits it. Never touches your project content. |

---

## How to use it

**Not sure where you are?** → run `/2ndbrain` — checks setup state and tells you the next step

**Capture anything** → drop it in `inbox/` and ask Claude to process it

**Start a working session** → say *"I need to work on [topic]"* — Claude creates a slug-based session under your SOW

**Generate a TLU** → run `/tlu <sow>` — Claude pulls from working sessions, meeting notes, and Jira status

**Track a stakeholder** → copy `stakeholders/_example/`, fill in `profile.md`

**Log a meeting** → ask Claude: *"log this meeting summary"* — saves to the right SOW

## Multi-contributor workflow

Multiple PMs or leads can share the same brain repo — each owning a different SOW — without stepping on each other.

**Branch model:**
- `main` is protected — requires a PR and one approval to merge
- Each SOW lead owns a long-lived branch: `sow1`, `sow2`, etc. Everyone working on that SOW uses the same branch.

**Day-to-day:**
- Work freely on your SOW branch — commit and push anytime, no PR needed
- Pull `main` into your branch regularly to pick up the other lead's updates: `git merge main`
- Open a PR from your SOW branch → `main` weekly (end of week, before a TLU, at a milestone)

**The weekly PR is more than a merge** — the diff is markdown: meeting summaries, stakeholder notes, TLU drafts. It tells the story of your week. The other lead approves in seconds and immediately sees what you've been working on, who you met with, and what's blocked. No extra syncs needed.

**If a push to main gets rejected by GitHub**, that's expected — Claude will set up your SOW branch for you.

**GitHub setup** (repo owner, one-time):
1. Give all contributors **Write** access (not Admin)
2. Protect `main`: require 1 PR approval, allow any collaborator to approve

## Notion channel

Each SOW can be connected to a Notion project page. Add the URL to `sows/<sow>/sow.config.yaml`:

```yaml
NOTION_PROJECT_URL: "https://app.notion.com/..."
```

Once set, two commands become available:

| Command | What it does |
|---------|-------------|
| `/publish-to-notion <file>` | Publishes a vault `.md` file to Notion as a child page. Updates the page if it already exists (matched by title). |
| `/fetch-from-notion [sow]` | Pulls all child pages from the Notion project page, traverses TLU history chains, and writes `notion-context.md`. |

`/bootstrap` also reads from Notion automatically when `NOTION_PROJECT_URL` is set.

**Requires:** Notion connector enabled in Claude settings (claude.ai → Integrations → Notion).

## SOW structure

Each SOW lives at `sows/<sow-name>/`:

| Directory | Purpose |
|-----------|---------|
| `<sow-name>-reference.md` | Scope, key dates, deliverables for this SOW |
| `work/` | Working sessions — slug-based, open-ended |
| `meeting-summaries/` | Dated meeting notes |
| `deliverables/` | Final deliverable artifacts |
| `sow.config.yaml` | Drive folders (comma-separated), meeting filter, Slack channels, Notion URL, engagement type/context |

To start a new SOW: copy `sows/_template/` and rename it. Or run `/bootstrap --sow <name>`.

## Requirements

- [Claude Code](https://claude.ai/code) — for AI-assisted project work
- A markdown editor — [Obsidian](https://obsidian.md) recommended (any editor works)
- Google Drive and Slack connected in Claude Code (for `/bootstrap`)
- Notion connected in Claude Code (optional — for `/publish-to-notion` and `/fetch-from-notion`)
- Network access to [`github.com/rabb1tl0ka/claude-skills`](https://github.com/rabb1tl0ka/claude-skills) (optional — `/bootstrap` pulls the `action-board` skill from there on first run; if the clone fails, `/bootstrap` still completes, it just skips that step and `action-board` won't be available until someone copies it in manually. `github-commit`, `github-branch-publish`, and `github-branch-refresh` are bundled with this template, so they need no network access.)
