# .kernel/ — Maintainer Tooling

This directory contains internal tooling for the `ai-project-2ndbrain` template repository. It is **not** part of the engagement brain and should be ignored by anyone who has forked this repo for a client engagement.

## Contents

| Item | Purpose |
|------|---------|
| `roadmap/` | Template repo improvement tracking (features, ideas, challenges) |
| `test-data/` | Synthetic ACME Corp scenario for validating the bootstrap flow |
| `upgrade.sh` | Upgrades a single existing 2ndbrain fork to the latest template version |
| `upgrade-all.sh` | Runs `upgrade.sh` across every client repo listed in `repos.txt` |
| `repos.txt` | Local, gitignored list of client repo paths to upgrade (copy from `repos.txt.example`) |
| `release.sh` | Cuts new template releases (bump version, tag, push) |
| `.2ndbrain-version` | Current template version stamp |
| `.roadmap-version` | Roadmap format version stamp |

If you forked this repo for a client engagement: nothing here is for you.
