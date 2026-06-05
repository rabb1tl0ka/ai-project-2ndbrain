---
status: done
priority: high
owner: ""
phase: ""
depends_on: []
---

# Feature: SOW Branch Config + SOW Lead Identity

## One-Line Overview

`/onboard` asks who the SOW lead is, records it in `sow.config.yaml`, and creates the long-lived `sow{N}` branch on GitHub — so Claude always knows where to direct commits and the branch exists from day one.

## What it does

### 1. `/onboard` asks for the SOW lead

During SOW setup, `/onboard` asks:
> "Who is the lead for this SOW? (the person responsible for delivery — e.g. `ronny`)"

Normalize to lowercase. Write to `sow.config.yaml`:
```yaml
sow_lead: ronny
```

This is committed and shared — it's a property of the SOW, not of the user.

### 2. Creates the long-lived `sow{N}` branch

After writing `sow_lead`, `/onboard` creates the branch if it doesn't exist:
```bash
git checkout -b sow3
git push -u origin sow3
git checkout -
```

Print explicit output to the user:
```
✓ Branch `sow3` created and pushed to origin.
  Team members should branch off `sow3` and PR back into it.
  You PR `sow3` → `main` periodically to sync with the rest of the engagement.
```

If the branch already exists, print:
```
✓ Branch `sow3` already exists on origin — skipped creation.
```

### 3. Suggests branch protection (optional)

After branch creation, print a suggestion to the SOW lead:
```
💡 Consider protecting `sow3` on GitHub to require PRs from team members
   (Settings → Branches → Add ruleset). This keeps contributions visible
   and avoids accidental direct pushes. Totally optional — skip if you're
   fine with direct pushes.
```

No enforcement. The lead decides.

## Branching model

```
main                          ← PR from sow{N}, other SOW lead approves
└── sow3 (long-lived)         ← Ronny has merge authority, created by /onboard
│   ├── sow3/alice-tlu-week3  ← short-lived, PR into sow3
│   └── sow3/james-kickoff    ← short-lived, PR into sow3
└── sow4 (long-lived)         ← Bruno has merge authority, created by /onboard
    ├── sow4/bruno-chore-x    ← short-lived, PR into sow4
    └── sow4/sarah-notes      ← short-lived, PR into sow4
```

- **SOW lead** has merge authority on `sow{N}` and PRs `sow{N}` → `main`
- **Team members** branch off `sow{N}/<name-or-slug>` and PR into `sow{N}`
- GitHub rulesets enforce what needs enforcing — Claude handles guidance

## How Claude uses `sow_lead`

When anyone asks Claude "where do I commit this?", Claude reads `sow_lead` from `sow.config.yaml` and gives a concrete answer:
> "Branch off `sow3` and open a PR into it. Ronny is the lead and will merge it."

No guessing, no wrong branch.

## What's out of scope

- Personal branch config per user — not needed, Claude derives it from the SOW dir name
- `/2ndbrain` checks for missing branch setup — GitHub will reject bad pushes; Claude recovers in context
- Bypass rights or special lead permissions — handled at GitHub ruleset level, not here

## Decisions

1. **`/onboard`, not `/bootstrap`** — this is a one-time setup question that belongs alongside other SOW config fields (`SLACK_CHANNELS`, `DRIVE_FOLDERS`). Bootstrap is for pulling data in.

2. **Branch name is derived, not stored** — `sow3` dir → `sow3` branch. No need to store it explicitly.

3. **Branch protection is a suggestion** — some leads are fine with direct pushes for chore commits. Enforcing it would add friction for no gain in those cases.

4. **SOW lead rotation** — when a lead rotates off, update `sow_lead` in `sow.config.yaml` via a PR and agree on who takes merge authority on the branch. A `/handover` checklist may be worth adding as a future feature.
