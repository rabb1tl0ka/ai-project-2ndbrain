---
name: github-branch-refresh
description: Merges the latest from a branch's parent (its SOW integration branch, or main) into the branch you're currently on, then pushes — always to your own branch, never opens a PR. Triggers on "/github-branch-refresh", "refresh my branch", "pull the latest into my branch", "sync my branch".
argument-hint: "[main] — omit to refresh from the branch's usual parent (the SOW branch); pass 'main' to pull main all the way down"
---

# /github-branch-refresh — pull the latest parent content into your branch

Works in any repo that follows a parent → child branch convention (e.g. `main` → `sow1-digital` → `sow1-digital-bruno`). Lets a contributor catch their branch up without knowing git commands or which upstream branch to merge from.

This skill never opens a PR — it only ever pushes to the branch you're already on. If GitHub rejects that push (branch protection), that's the signal this branch wasn't yours to push to directly; see Step 3.

## Step 0 — Parse arguments

- No argument: refresh from this branch's usual parent.
- `main`: refresh from `main` instead (useful when the current branch is itself a SOW integration branch, or when a contributor wants main's changes pulled all the way down before the usual parent has synced yet).

## Step 1 — Determine current branch and its parent

- Read the current branch: `git branch --show-current`.
- Determine the parent per this repo's own `CLAUDE.md` convention:
  - A personal branch (e.g. `<sow>-<name>`) → its parent is the SOW integration branch (`<sow>`).
  - A SOW integration branch (e.g. `sow1-digital`) → its parent is `main`.
- If an argument was passed (`main`), use that as the parent instead of the derived one.
- If the convention can't be determined (no matching pattern, no documented convention), ask which branch to merge from — never guess silently.

## Step 2 — Fetch and merge

```bash
git fetch origin
git merge origin/<parent> --no-edit
```

- Merge, never rebase (this repo's convention — rebase replays commits and causes conflicts when the same changes already landed via a different branch).
- If the merge conflicts, stop here and report it. Don't attempt to resolve conflicts automatically — hand it back to the user with the list of conflicting files.
- If already up to date, report that and stop — nothing to push.

## Step 3 — Push

```bash
git push origin <current-branch>
```

- Success: report what moved (commit range or "already up to date").
- Rejected by GitHub (branch protection, e.g. "Changes must be made through a pull request"): this means the current branch isn't one you can push to directly. Report the rejection plainly, and suggest either:
  - Checking out your own personal branch and running this skill there instead, or
  - Using `/github-branch-publish` to open a PR if updating the shared branch is actually what was intended.
  - Do not attempt to bypass the rejection — no `--force`, no admin overrides, no retries. GitHub's rule is the actual source of truth for who can push where; the skill just reports what it says.

## Non-negotiables

- Never rebase.
- Never force-push.
- Never open a PR from this skill — that's `/github-branch-publish`'s job. This one only ever pushes to the branch already checked out.
- Never resolve merge conflicts automatically — surface them and stop.
