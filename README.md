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
project.config.example.yaml  ← config template
project.config.yaml          ← your project config, gitignored — never committed
setup.sh                     ← applies your config and creates your first SOW
```

## Setup

**1. Clone**
```bash
git clone https://github.com/rabb1tl0ka/ai-project-2ndbrain
cd ai-project-2ndbrain
```

**2. Fill in your config**

Run setup once to generate your config file:
```bash
./setup.sh
```

On first run, it creates `project.config.yaml` and exits. Fill in your details — 8 fields, takes 2 minutes:

```yaml
PROJECT_NAME: "Acme Corp"
CLIENT_NAME: "Acme Corp Inc."
ENGAGEMENT_TYPE: "GenAI Assessment"
ENGAGEMENT_CONTEXT: "Loka is assessing Acme Corp's AI infrastructure and producing a modernization roadmap."
OWNER_NAME: "Your Name"
OWNER_HANDLE: "@yourhandle"
OWNER_ROLE: "TPM"
FIRST_SOW: "sow1"
```

`project.config.yaml` is gitignored — your config is never committed.

**3. Run setup again**
```bash
./setup.sh
```

Replaces all `{{placeholders}}` in the vault with your values and creates your first SOW directory.

**4. Push to your project's GitHub**

```bash
git remote set-url origin <your-new-repo-url>
git add -A && git commit -m "init: configure project brain"
git push -u origin main
```

Create a fresh repo for this project — don't push back to this template.

**5. Open the vault and spawn Claude Code**

Open `project-vault/` in Obsidian (or any markdown editor).

Then start a Claude Code session inside it:
```bash
cd project-vault
claude
```

Claude reads `CLAUDE.md` automatically and knows how the brain works.

**6. Fill in your context**

Open `project-vault/CLAUDE.md` and complete the team and stakeholder sections. This is what makes the brain smart about your specific engagement.

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
- `bash` + `sed` — for `setup.sh` (standard on macOS and Linux)
