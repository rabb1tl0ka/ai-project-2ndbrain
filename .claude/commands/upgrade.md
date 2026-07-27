Check for updates to the ai-project-2ndbrain template and apply them if available.

This command updates tooling only — commands, templates, conventions. It never touches your project content: SOW dirs, stakeholders, team, notes, inbox, archive. Root `CLAUDE.md` is a special case (see Step 4b bis): it's placeholder-substituted by `/onboard` with real client values, so template updates to it are merged in placeholder-aware, not blind-copied — local hand-edits are preserved and only flagged as a conflict if they can't be reconciled automatically.

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
  -- .claude/commands/ .claude/skills/ templates/ sows/_template/ roadmap/CLAUDE.md roadmap/templates/ config.example.yaml README.md CLAUDE.md \
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
- `.claude/skills/` (bundled skills — github-commit, github-branch-publish, github-branch-refresh)
- `.claude/commands/2ndbrain.md`
- `.claude/commands/onboard.md`
- `.claude/commands/bootstrap.md`
- `.claude/commands/meeting-recap.md`
- `.claude/commands/meeting-recap-drive.md`
- `.claude/commands/publish-to-notion.md`
- `.claude/commands/fetch-from-notion.md`
- `.claude/commands/sync-tasks.md`
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

### 4b bis — Merge root CLAUDE.md (placeholder-aware, not a blind checkout)

Root `CLAUDE.md` is filled in by `/onboard`'s repo-wide `{{KEY}}` substitution (client name, owner, SOW list, etc.), so it can't be blind-copied like the files above — that would revert the file back to raw placeholders. Merge it instead:

1. Get the template's current version: `git show 2ndbrain-template/main:CLAUDE.md`.
2. Find every `{{KEY}}` token in that template content. Build a pattern where each `{{KEY}}` matches any text and everything else must match literally, then test whether the local `CLAUDE.md` matches that pattern in full (start to end).
3. **If it matches** (the only differences are placeholder substitutions — no real hand-edits): extract each `{{KEY}}` → value pair from the local file, apply those same substitutions to the new template content, and write the result over local `CLAUDE.md`. This is the common case and needs no confirmation.
4. **If it doesn't match** (the local file has real edits beyond placeholder differences — new sections, reworded rules, anything added or changed by hand): this is a conflict, not an error. Ask the user via `AskUserQuestion`:
   - **Overwrite** — replace with the template's version (placeholders reapplied), losing the local hand-edits — say so plainly.
   - **Keep local as-is** — skip `CLAUDE.md` entirely, leave it untouched.
   - **Show full diff first** — print the diff between local and the would-be-merged version, then ask again.
   Apply whichever the user picks. Do not guess or silently pick a side.
5. Track whether `CLAUDE.md` was actually changed (merged or overwritten) — only stage it in 4d if so.

### 4c — Update version stamp

```bash
echo "{{latest_version}}" > .kernel/.2ndbrain-version
```

### 4d — Commit

```bash
git add .claude/commands/ .claude/skills/ config.example.yaml README.md \
        sows/_template/ templates/ roadmap/CLAUDE.md roadmap/templates/ \
        .kernel/.2ndbrain-version
# Only if 4b bis actually changed it (merged or user chose overwrite):
git add CLAUDE.md
git commit -m "chore: upgrade ai-project-2ndbrain {{current_version}} → {{latest_version}}"
```

Report:
```
✓ Upgraded to {{latest_version}}.

Tooling updated:
  .claude/commands/     — all commands
  .claude/skills/       — bundled skills
  config.example.yaml   — config reference
  sows/_template/       — SOW config and reference templates
  templates/            — meeting summary, TLU, working session templates
  roadmap/              — roadmap conventions and item templates
  CLAUDE.md             — merged (placeholders reapplied) | kept as-is | overwritten, per Step 4b bis

Your other project content (SOW dirs, stakeholders, team, notes, inbox, archive) was not touched.

Review the diff before pushing: git show HEAD
```

---

## Notes

- To create a PR instead of a direct commit, stage the changes and push the branch manually before committing — or ask Claude to do it.
- The `2ndbrain-template` remote is left in place after upgrade so future runs skip the `remote add` step.
- Root `CLAUDE.md` is merged placeholder-aware (Step 4b bis), not blind-copied — it contains real client values after `/onboard` runs, and may also contain the user's own hand-written sections that must survive an upgrade.
