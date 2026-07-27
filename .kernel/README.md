# .kernel/ — Maintainer Tooling

This directory contains internal tooling for the `ai-project-2ndbrain` template repository. It is **not** part of the engagement brain and should be ignored by anyone who has forked this repo for a client engagement.

## Contents

| Item | Purpose |
|------|---------|
| `roadmap/` | Template repo improvement tracking (features, ideas, challenges) |
| `test-data/` | Synthetic ACME Corp scenario for validating the bootstrap flow |
| `template-upgrade-repos.yaml` | Local, gitignored list of client repo paths to upgrade (copy from `template-upgrade-repos-example.yaml`) |
| `release.sh` | Cuts new template releases (bump version, tag, push) |
| `.2ndbrain-version` | Current template version stamp |
| `.roadmap-version` | Roadmap format version stamp |

Pushing tooling updates out to client repos is done with `/template-upgrade-repos` (see `.claude/commands/template-upgrade-repos.md`), run from a Claude Code session in this repo. It replaced the old `upgrade.sh`/`upgrade-all.sh` scripts, which did a blind file copy and could silently overwrite client-specific customizations (a custom `.gitignore` entry, an onboarding-filled placeholder inside a copied command file). The command diffs before touching anything and asks before overwriting anything it can't safely reconcile on its own.

If you forked this repo for a client engagement: nothing here is for you.
