---
status: todo
priority: high
owner: ""
phase: ""
depends_on: []
---

# Feature: SOW Branch Config + Contributor Identity

## One-Line Overview
Bootstrap captures each contributor's SOW branch name into `config.yaml` so Claude always knows where to commit, and `/2ndbrain` warns when the branch is missing or unconfigured.

## What's the idea

When a contributor bootstraps a SOW, Claude asks for their name (if they're not the repo owner) and records their SOW branch in the gitignored `config.yaml`. On every subsequent session, Claude verifies the branch exists in git and warns if not. `/2ndbrain` surfaces this as a setup gap.

### Branching model (two-tier)

```
main
├── sow3              ← Ronny's canonical SOW3 branch (Ronny works here freely)
│   ├── sow3/sarah   ← Sarah (Ronny's team) PRs into sow3
│   └── sow3/james   ← James (Ronny's team) PRs into sow3
└── sow4              ← Bruno's canonical SOW4 branch (Bruno works here freely)
    └── sow4/alice   ← Alice (Bruno's team) PRs into sow4
```

- SOW lead owns the `sow{N}` branch — works and pushes freely, no PR needed
- Team members branch off `sow{N}/<name>` and PR into `sow{N}`
- SOW leads PR `sow{N}` into `main` periodically (other SOW lead approves)

### Branch naming rules

| Who | Branch |
|-----|--------|
| Repo owner bootstrapping their own SOW | `sow{N}` |
| Any other contributor | `sow{N}/<their-name>` |

### `config.yaml` addition

```yaml
sow_branches:
  sow3: sow3/ronny    # or just "sow3" if Ronny is repo owner
  sow4: sow4/bruno
```

### Bootstrap changes

1. After SOW selection, always ask: "Who are you bootstrapping this SOW for? Enter your own name if it's for you. (e.g. `Bruno` or `Ronny`)"
2. Normalize the name to lowercase for branch naming (`Bruno` → `bruno`)
3. Compare normalized name against normalized `owner_name` from `config.yaml`
4. Derive branch name: `sow{N}` if names match (they're the SOW lead), `sow{N}/<name>` otherwise
5. Write to `config.yaml` under `sow_branches`
6. If branch doesn't exist in git yet: offer to create it (`git checkout -b <branch>`)

### Session start / `/2ndbrain` checks

For each SOW in `sow_branches`:
- Branch in config but not in git locally → warn: "your SOW branch `sow4/bruno` isn't in git — run `git checkout -b sow4/bruno` or I can do it for you"
- Branch not in config at all → prompt to run `/bootstrap` for that SOW
- Branch exists in both → silent pass

## Expected advantages / benefits

- Claude always knows which branch to commit to — no accidental pushes to main
- Contributors on a shared SOW have clear lanes (`sow4` vs `sow4/alice`)
- `/2ndbrain` catches "not set up yet" before it becomes a push-rejection surprise
- Gitignored config means no merge conflicts over branch names

## Downsides / risks

- Adds a question to bootstrap flow — minor friction on first run
- Two-tier PRs (team → SOW branch → main) may feel heavy for very small teams; optional for teams of 2

## What's been tried already

None yet. Collaboration model was just designed and documented in `CLAUDE.md` (June 2026).

## Open questions

1. Should `sow{N}` branch protection be enforced on GitHub (require PR from `sow{N}/<name>`)? Or is that optional per engagement?
2. How does a team member bootstrap — do they run `/bootstrap` fresh, or does the SOW lead share a pre-bootstrapped repo?
3. Should Claude offer to create the `sow{N}/<name>` branch automatically at the end of bootstrap, or just document it?
4. What happens when someone's name changes or they rotate off? (cleanup path for stale branches)
