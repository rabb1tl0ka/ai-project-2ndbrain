---
status: todo
priority: high
owner: ""
phase: ""
depends_on: []
---

# Feature: SOW Branch Config + Contributor Identity

## One-Line Overview
Bootstrap records the SOW lead per SOW in `sow.config.yaml` and each user's personal branch in gitignored `config.yaml`, so Claude always knows where to commit and `/2ndbrain` warns when setup is incomplete.

## What's the idea

Each SOW has a designated lead — the person who pushes freely to that SOW's branch. Bootstrap asks who the lead is (once, when first setting up a SOW) and stores it in `sow.config.yaml`. Each user also records their own branch in their local gitignored `config.yaml`. On every session, Claude verifies the branch exists in git. `/2ndbrain` surfaces missing setup as a gap.

### Branching model (two-tier)

```
main
├── sow3              ← Ronny (SOW3 lead) pushes freely here
│   ├── sow3/sarah   ← Sarah PRs into sow3
│   └── sow3/james   ← James PRs into sow3
└── sow4              ← Bruno (SOW4 lead) pushes freely here
    └── sow4/alice   ← Alice PRs into sow4
```

- **SOW lead** owns `sow{N}` — commits and pushes freely, no PR needed to the SOW branch
- **Team members** branch off `sow{N}/<name>`, PR into `sow{N}`
- **SOW leads** PR `sow{N}` → `main` periodically; the other SOW lead (or repo owner) approves

### What defines the SOW lead

The SOW lead is whoever is responsible for that SOW's delivery — not necessarily the repo owner. The repo owner may or may not be a SOW lead. Examples:

| Person | Repo owner | SOW lead | Branch |
|--------|-----------|----------|--------|
| Bruno | yes | SOW4 | `sow4` |
| Ronny | no | SOW3 | `sow3` |
| Alice | no | neither | `sow4/alice` |

The SOW lead is set once at bootstrap time and stored in `sow.config.yaml` (committed, shared). It is a property of the SOW, not of the user.

### Storage: two files, two concerns

**`sow.config.yaml`** (committed, per-SOW) — stores who the lead is:
```yaml
sow_lead: ronny   # normalized lowercase
```

**`config.yaml`** (gitignored, per-user) — stores this user's branch:
```yaml
sow_branches:
  sow3: sow3/ronny
  sow4: sow4/bruno
```

### Branch naming rules

| Who | Branch |
|-----|--------|
| SOW lead (as recorded in `sow.config.yaml`) | `sow{N}` |
| Anyone else | `sow{N}/<their-name>` |

### Bootstrap changes

**When setting up a SOW for the first time (no `sow_lead` in `sow.config.yaml`):**

1. Ask: "Who is the lead for this SOW? (the person who owns delivery and will push freely to `sow{N}`)"
2. Normalize to lowercase (`Ronny` → `ronny`)
3. Write `sow_lead: ronny` to `sow.config.yaml` — this is committed and shared

**Then, for the person running bootstrap:**

4. Ask: "Who are you? Enter your name. (e.g. `Bruno` — used to set up your personal branch)"
5. Normalize to lowercase
6. Compare against `sow_lead`: if match → their branch is `sow{N}`, otherwise `sow{N}/<name>`
7. Write to `config.yaml` under `sow_branches`
8. Create the branch automatically: `git checkout -b <branch> && git push -u origin <branch>`

**When a SOW already has a lead recorded** (someone else ran bootstrap first):

- Skip the SOW lead question, show who the lead is
- Go straight to "Who are you?" and derive the personal branch

### Session start / `/2ndbrain` checks

For each SOW directory found under `sows/`:
- `sow.config.yaml` has no `sow_lead` → flag: "SOW lead not set — run `/bootstrap` for this SOW"
- `config.yaml` has no entry for this SOW → flag: "your branch for `sow{N}` isn't configured — run `/bootstrap`"
- Branch in `config.yaml` but not in git locally → warn: "branch `sow4/bruno` isn't in git — want me to create it?"
- Everything present → silent pass

## Expected advantages / benefits

- Claude always knows which branch to commit to — no accidental pushes to main
- SOW lead is explicit and committed — no ambiguity about who owns the SOW branch
- Team members have clear lanes (`sow4/alice` PRs into `sow4`)
- `/2ndbrain` catches missing setup before it becomes a push-rejection surprise
- Personal branch config is gitignored — no merge conflicts

## Downsides / risks

- Two questions added to bootstrap (SOW lead + personal name) — minor friction on first run
- Two-tier PRs (team → SOW branch → main) adds overhead for very small teams; optional for teams of 2
- `sow_lead` in `sow.config.yaml` is committed — changing it requires a PR, which is intentional but worth noting

## What's been tried already

None yet. Collaboration model designed and documented in `CLAUDE.md` (June 2026).

## Decisions

1. **SOW branch protection on GitHub**: Yes — protect `sow{N}` branches to require PRs from `sow{N}/<name>` contributors. GitHub supports branch protection rules with wildcard patterns (e.g. `sow*`). This keeps the SOW lead aware of all team contributions and prevents accidental overlaps. Bootstrap instructions should include setting this up.

2. **Who bootstraps**: Whoever runs bootstrap first becomes the de-facto SOW branch master. Doesn't have to be the PM — can be the Tech Lead if the PM isn't technical. The key is that one person does it and the `sow_lead` gets recorded correctly.

3. **Branch creation**: Bootstrap creates the branch automatically (`git checkout -b <branch> && git push -u origin <branch>`) — no manual step for the user.

4. **SOW lead rotation**: When a SOW lead rotates off, there's a handover process — the repo owner inherits the SOW branch or it's transferred to the incoming lead. This requires updating `sow_lead` in `sow.config.yaml` (via PR) and agreeing on branch ownership. A `/handover` command or checklist may be worth adding as a future feature.
