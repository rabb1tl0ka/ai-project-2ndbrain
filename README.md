# AI Project 2nd Brain

A Claude-powered engagement knowledge system for Loka projects. Fork it, configure it in 2 minutes, and have a working brain that Claude understands from day one.

Structured the way a TPM thinks — so whether you're an ML Lead, Tech Lead, or shadowing engineer, the brain helps you work like a TPM would: tracking stakeholders, organizing by SOW, running working sessions, and generating TLUs.

## What's inside

```
inbox/               ← raw captures land here first
sows/                ← one directory per SOW
  _template/         ← copy this to create a new SOW
stakeholders/        ← client stakeholder profiles
team/                ← Loka team member profiles
roadmap/             ← challenges, ideas, features for this engagement
notes/               ← project-level thinking and context
archive/             ← processed inbox items worth keeping
templates/           ← working session, meeting summary, TLU templates
config.example.yaml  ← config reference (3 fields)
config.yaml          ← your engagement config, gitignored — never committed
```

## Setup

**1. Fork and clone**

Fork this repo on GitHub (one fork per engagement), then clone your fork:
```bash
git clone https://github.com/<your-org>/<your-project>-ai-2ndbrain
cd <your-project>-ai-2ndbrain
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

Open `notes/project-context.md` — that's your ground truth. Fill in team profiles in `team/`, enrich stakeholder profiles in `stakeholders/`, and address any tensions flagged by bootstrap.

**5. Commit and push**

```bash
git add -A && git commit -m "init: configure engagement brain"
git push
```

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
| `/meeting-recap` | Picks up new Gemini meeting notes from Drive since last run. Incremental — only processes what's new. |
| `/meeting-recap --keywords <words>` | Search for specific keywords in recent meetings. |
| `/meeting-recap --date <date>` | Fetch meetings from a specific date. |

### Notion

| Command | What it does |
|---------|-------------|
| `/publish-to-notion <file>` | Publishes any vault `.md` file to Notion as a child page of the SOW's project page. Idempotent — republishing updates the existing page. |
| `/fetch-from-notion [sow]` | Pulls all child pages from the Notion project page, traverses TLU history chains, writes `notion-context.md`. |

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

**Generate a TLU** → say *"generate this week's TLU"* — Claude pulls from working sessions and meeting notes

**Track a stakeholder** → copy `stakeholders/_example/`, fill in `profile.md`

**Log a meeting** → ask Claude: *"log this meeting summary"* — saves to the right SOW

**Track an idea or challenge** → ask Claude: *"save this as an idea"* — goes to `roadmap/`

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
