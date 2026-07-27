Maintainer-only. Pushes the latest `ai-project-2ndbrain` tooling files from this template repo into one or more already-bootstrapped client repos, without clobbering client-specific customizations.

Replaces the old `.kernel/upgrade.sh` / `upgrade-all.sh` scripts, which did a blind `cp` and silently destroyed things like custom `.gitignore` entries and onboarding-filled placeholders inside copied files (e.g. `.claude/commands/bootstrap.md` contains a `{{CLIENT_NAME}}` example snippet that `/onboard`'s repo-wide `sed` fills in with the real client name — a plain overwrite reverts it to the raw placeholder).

## Usage

```
/template-upgrade-repos [target-repo-path]
```

- No argument: read the `repos:` list from `.kernel/template-upgrade-repos.yaml` (`~` supported per entry) and upgrade each in turn.
- With an argument: upgrade just that one repo, ignoring the config file.

If `.kernel/template-upgrade-repos.yaml` doesn't exist and no argument was given, tell the user to `cp .kernel/template-upgrade-repos-example.yaml .kernel/template-upgrade-repos.yaml` and fill it in, then stop.

---

## Step 1 — Resolve targets and version info

Expand `~` in each target path. For each target, validate before doing anything else:
- Directory must exist and contain `.git` — otherwise report and skip to the next target.
- Must contain `CLAUDE.md` and `sows/` — otherwise report "doesn't look like an ai-project-2ndbrain repo" and skip.
- Run `git -C <target> diff --quiet` and `git -C <target> diff --cached --quiet`; if either is dirty, warn "has uncommitted changes — continuing anyway" (don't block).

Version info (compute once, shared across all targets):
- `CURRENT_TAG` = `git describe --tags --abbrev=0` in this template repo.
- Per target, `LAST_TAG` = contents of `<target>/.kernel/.2ndbrain-version`, or `v0 (unknown)` if missing.

## Step 2 — The tooling file list

Same files the old script copied — this is the full sync set:

```
.claude/commands/2ndbrain.md
.claude/commands/onboard.md
.claude/commands/bootstrap.md
.claude/commands/meeting-recap.md
.claude/commands/meeting-recap-drive.md
.claude/commands/publish-to-notion.md
.claude/commands/fetch-from-notion.md
.claude/commands/upgrade.md
config.example.yaml
README.md
sows/_template/sow.config.yaml
sows/_template/sow-reference.md
templates/ (whole directory)
.gitignore
```

`.kernel/upgrade.sh` is no longer part of this list — that script is retired (see `.kernel/README.md`).

## Step 3 — Per-file classification

For each file in the list, against each target repo, read both the template's copy (source) and the target's copy (destination, if it exists). Classify:

**a. Missing in target** → copy it as-is (`mkdir -p` the parent dir first). Log `+ <path> (new)`.

**b. Byte-identical** → skip silently. Log nothing (or a single collapsed "up to date" line at the end, don't spam per-file).

**c. `.gitignore`, and it differs** → never overwrite. Merge additively:
   - Split both into lines.
   - Append any source line that isn't already present verbatim in the destination (trailing slash differences like `private/` vs `private` count as *different* lines — add the source line too rather than trying to normalize; the user can dedupe by hand if they want).
   - Preserve all existing destination lines and their order; new lines go at the end.
   - Write the merged result. Log `~ .gitignore (merged N new line(s): ...)`.

**d. Any other file that differs — check if it's a placeholder-substitution-only diff:**
   - Take the source content and find all `{{KEY}}` tokens.
   - Build a version of the source where every `{{KEY}}` is replaced by a wildcard match, and everything else (including regex metacharacters) is treated as literal text to match exactly.
   - Test whether the destination content matches that pattern in full (start to end, not just a substring).
   - If it matches: extract each `{{KEY}}` → matched-value pair from the destination. Apply those same substitutions to the *new* source content (so template changes land, but the client's real values are re-applied) and write that. Log `~ <path> (upgraded, placeholders reapplied: KEY=value, ...)`.
   - If it does NOT match (real edits, structural differences, or values that don't cleanly correspond to `{{KEY}}` tokens): this is a genuine conflict. Do not touch the file. Add it to a `conflicts` list for this target with both versions' content (or a `git diff --no-index`-style diff) — don't resolve it yet.

## Step 4 — Resolve conflicts

After classifying every file for a target, if `conflicts` is non-empty, show the user a summary (file path + short diff) for *all* conflicts across *all* targets in one batch — don't interrupt per-file or per-repo. For each conflicting file ask, via `AskUserQuestion`:

- **Overwrite** — replace with the template's version (client's edits are lost — say so plainly).
- **Keep target as-is** — skip this file entirely, leave it untouched.
- **Show full diff first** — print the complete diff, then ask again (overwrite / keep).

Apply the user's choice per file. Log the outcome.

## Step 5 — Backfill new SOW config fields

Same as before — this part is purely additive and has no conflict risk, so no need to ask:

For every `<target>/sows/*/sow.config.yaml` except `sows/_template/sow.config.yaml`: if it doesn't already contain a `TASK_BOARD_FOLDER_ID:` key, append:

```

# Google Drive folder ID where /sync-tasks drops task board snapshots.
# Should be a Loka-internal folder, NOT one shared with the client.
# If empty, /sync-tasks will ask for a folder URL before proceeding.
TASK_BOARD_FOLDER_ID: ""
```

Log `+ sows/<sow>/sow.config.yaml — added TASK_BOARD_FOLDER_ID`.

## Step 6 — Version stamp

Write `<target>/.kernel/.2ndbrain-version` = `CURRENT_TAG`.

## Step 7 — Report, per target

```
=== <target> ===
<LAST_TAG> → <CURRENT_TAG>

  + <new files>
  ~ <merged/upgraded files, with what changed>
  ⏭  <files left untouched due to a "keep" choice>
  ✓ up to date: N file(s)

Review the diff, then:
  cd <target>
  git add <touched paths>
  git commit -m 'chore: upgrade ai-project-2ndbrain <LAST_TAG> → <CURRENT_TAG>'
```

Never `git add` or commit automatically — that stays a manual step for the user, same as before. Don't offer a `--create-pr` mode unless asked; if useful later it can be added back.

At the very end, across all targets, print a one-line totals summary: repos processed, files auto-merged, files left for manual resolution.

---

## Notes

- This command is maintainer tooling — it's never part of the file list it copies, so running it never ships itself into a client repo.
- If a genuinely new kind of conflict shows up that doesn't fit "identical / gitignore / placeholder-only / real edit", stop and ask the user how to classify it rather than guessing.
