Check for updates to the ai-project-2ndbrain template and apply them if available.

This command updates tooling only — commands, templates, conventions. It never touches your project content: CLAUDE.md (post-onboard), SOW dirs, stakeholders, team, notes, inbox, archive.

---

## Step 1 — Check current version

Read `.kernel/.2ndbrain-version`. If the file doesn't exist, treat current version as `v0 (unknown)`.

---

## Step 2 — Check latest version on the template repo

Run:

```bash
git ls-remote --tags https://github.com/rabb1tl0ka/ai-project-2ndbrain
```

Parse the output to find the latest semver tag (highest vX.Y.Z). If this fails (no network, repo moved), stop:
> "⚠ Couldn't reach the template repo. Check your connection and try again."

---

## Step 3 — Compare and report

If current version matches latest:
```
✓ You're up to date ({{current_version}}).
```
Stop here.

If behind:
```
Update available: {{current_version}} → {{latest_version}}

Run /upgrade --apply to pull in the latest tooling.
```

Also show a summary of commits between the two versions:
```bash
git log {{current_version}}..{{latest_version}} --oneline \
  -- .claude/commands/ templates/ sows/_template/ roadmap/CLAUDE.md roadmap/templates/ config.example.yaml README.md \
  2>/dev/null || echo "(changelog unavailable — tags may differ)"
```
Use the template repo's git history for this: fetch tags first if needed.

---

## Step 4 — Apply (only when `--apply` flag is passed)

### 4a — Register the template as a remote

```bash
git remote add 2ndbrain-template https://github.com/rabb1tl0ka/ai-project-2ndbrain 2>/dev/null || true
git fetch 2ndbrain-template main --tags --quiet
```

### 4b — Copy tooling files from the template

For each file below, run:
```bash
git checkout 2ndbrain-template/main -- <file>
```

Files to update:
- `.claude/commands/2ndbrain.md`
- `.claude/commands/onboard.md`
- `.claude/commands/bootstrap.md`
- `.claude/commands/meeting-recap.md`
- `.claude/commands/publish-to-notion.md`
- `.claude/commands/fetch-from-notion.md`
- `.claude/commands/upgrade.md`
- `config.example.yaml`
- `README.md`
- `sows/_template/CLAUDE.md`
- `sows/_template/sow.config.yaml`
- `sows/_template/sow-reference.md`
- `templates/meeting-summary.md`
- `templates/tlu.md`
- `templates/working-session.md`
- `roadmap/CLAUDE.md`
- `roadmap/templates/template-feat.md`
- `roadmap/templates/template-idea.md`
- `roadmap/templates/template-challenge.md`

If any file doesn't exist on the remote (new file not yet in this version), skip it silently.

### 4c — Update version stamp

```bash
echo "{{latest_version}}" > .kernel/.2ndbrain-version
```

### 4d — Commit

```bash
git add .claude/commands/ config.example.yaml README.md \
        sows/_template/ templates/ roadmap/CLAUDE.md roadmap/templates/ \
        .kernel/.2ndbrain-version
git commit -m "chore: upgrade ai-project-2ndbrain {{current_version}} → {{latest_version}}"
```

Report:
```
✓ Upgraded to {{latest_version}}.

Tooling updated:
  .claude/commands/     — all commands
  config.example.yaml   — config reference
  sows/_template/       — SOW config and reference templates
  templates/            — meeting summary, TLU, working session templates
  roadmap/              — roadmap conventions and item templates

Your project content was not touched.

Review the diff before pushing: git show HEAD
```

---

## Notes

- To create a PR instead of a direct commit, stage the changes and push the branch manually before committing — or ask Claude to do it.
- The `2ndbrain-template` remote is left in place after upgrade so future runs skip the `remote add` step.
- CLAUDE.md is intentionally excluded — it contains real client values after `/onboard` runs.
