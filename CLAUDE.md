# Project Brain — Repo Onboarding

You are helping someone set up an AI-powered project 2nd brain for a client engagement.

## What this repo is

A ready-to-use project knowledge system. Clone it, fill in a config file, run setup, and have a working project brain that Claude understands from day one. Structured the way a TPM thinks — so even if you're an ML lead, a Tech Lead, or a shadowing engineer, the brain helps you work like a TPM would: tracking stakeholders, managing SOWs, running working sessions, and generating status updates.

## Key files

| File | Purpose |
|------|---------|
| `README.md` | Full setup instructions — read this first |
| `project.config.example.yaml` | Config reference |
| `project.config.yaml` | Your project config — gitignored, never committed |
| `.claude/commands/onboard.md` | `/onboard` — guided setup, run from the repo root |
| `project-vault/` | The actual project brain — open in Obsidian or any markdown editor |

## How to help a new user

When someone says "help me get started" or "read the README":

1. Read `README.md` in full
2. Walk them through setup conversationally
3. Tell them to run `/onboard` — it asks each config field, writes `project.config.yaml`, replaces placeholders, and creates the first SOW
4. Once onboarding is done, tell them to `cd project-vault && claude` and run `/bootstrap`
5. Point them to `project-vault/CLAUDE.md` to understand how to work inside the brain

## Common questions

- **"What is this?"** — A project knowledge system built around how Loka engagements actually run: SOWs, working sessions, stakeholders, TLUs, and a roadmap. Claude understands the structure.
- **"Do I need Obsidian?"** — No. Any markdown editor works. Obsidian is recommended.
- **"I'm not a TPM — is this for me?"** — Yes. The structure instills TPM habits (stakeholder tracking, SOW organization, status updates) without requiring TPM experience. Fill in what you know, Claude handles the rest.
- **"After onboarding, what do I do?"** — Run `/bootstrap` from inside `project-vault/`. It loads the SOW, meeting notes, and Slack history into the vault.
- **"What's `.kernel/`?"** — Internal repo tooling for the maintainer. Ignore it.

## What you should NOT do

- Don't help with vault content here — that happens inside `project-vault/` with its own Claude session
- Don't suggest editing `project-vault/` before running setup — placeholders need to be replaced first
- Don't expose `.kernel/` internals unless explicitly asked
