# AI Project 2nd Brain

A Claude-powered project knowledge system for Loka engagements. Clone it, configure it in 2 minutes, and have a working project brain that Claude understands from day one.

Structured the way a TPM thinks — so whether you're an ML Lead, Tech Lead, or shadowing engineer, the brain helps you work like a TPM would: tracking stakeholders, organizing by SOW, running working sessions, and generating TLUs.

## What's inside

```
project-vault/         ← your project brain (open this in Obsidian)
  inbox/               ← raw captures land here first
  sows/                ← one directory per SOW
    _template/         ← copy this to create a new SOW
  stakeholders/        ← client stakeholder profiles
  team/                ← Loka team member profiles
  roadmap/             ← challenges, ideas, features for this engagement
  notes/               ← project-level thinking and context
  archive/             ← processed inbox items worth keeping
  templates/           ← working session, meeting summary, TLU templates
project.config.example.yaml  ← config reference
project.config.yaml          ← your project config, gitignored — never committed
```

## Setup

**1. Fork and clone**

Fork this repo on GitHub (one fork per project engagement), then clone your fork:
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

Claude will ask you for each config value, write `project.config.yaml`, replace all `{{placeholders}}` in the vault, and create your first SOW directory. Takes about 2 minutes.

`project.config.yaml` is gitignored — your config is never committed.

**3. Commit and push**

```bash
git add -A && git commit -m "init: configure project brain"
git push
```

**4. Enter the vault and bootstrap**

```bash
cd project-vault
claude
```

Then run:
```
/bootstrap
```

This pulls in the SOW document, all historical meeting notes from Google Drive, and recent Slack history — then generates a context snapshot, stakeholder stubs, and a tensions/gaps report between what the SOW commits to and what's actually happening in the project.

**5. Fill in any gaps**

Open `notes/project-context.md` — that's your ground truth. Fill in team profiles in `team/`, enrich stakeholder profiles in `stakeholders/`, and address any tensions flagged by bootstrap.

## How to use it

**Capture anything** → drop it in `inbox/` and ask Claude to process it

**Start a working session** → say *"I need to work on [topic]"* — Claude creates a slug-based session under your SOW

**Generate a TLU** → say *"generate this week's TLU"* — Claude pulls from working sessions and meeting notes

**Track a stakeholder** → copy `stakeholders/_example/`, fill in `profile.md`

**Log a meeting** → ask Claude: *"log this meeting summary"* — saves to the right SOW

**Track an idea or challenge** → ask Claude: *"save this as an idea"* — goes to `roadmap/`

## SOW structure

Each SOW lives at `sows/<sow-name>/`:

| Directory | Purpose |
|-----------|---------|
| `<sow-name>-reference.md` | Scope, key dates, deliverables for this SOW |
| `work/` | Working sessions — slug-based, open-ended |
| `meeting-summaries/` | Dated meeting notes |
| `deliverables/` | Final deliverable artifacts |

To start a new SOW: copy `sows/_template/` and rename it.

## Requirements

- [Claude Code](https://claude.ai/code) — for AI-assisted project work
- A markdown editor — [Obsidian](https://obsidian.md) recommended (any editor works)
- Google Drive and Slack connected in Claude Code (for `/bootstrap`)
