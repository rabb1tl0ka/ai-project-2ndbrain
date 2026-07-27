Maintainer-only. Runs the full loop for landing a template change in this repo: commit (grouped, approved), push, then cut a release — so a template edit never sits committed-but-unreleased, which leaves `/template-upgrade-repos` diffing against a stale tag.

## Usage

```
/template-commit-n-release [vX.Y.Z]
```

- No argument: infer the version bump from conventional-commit prefixes and confirm with the user before releasing.
- With an argument: skip inference and pass that version straight to `.kernel/release.sh`, still asking for final confirmation.

## Step 1 — Commit

Run the same flow as `/github-commit` against the current working tree: group changes by theme, propose one commit message per group, get one approval on the whole batch, then stage and commit each group in sequence. Follow that skill's rules verbatim (never wildcard-add, never commit secrets, mirror this repo's commit style, `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>` trailer).

If the working tree is already clean (nothing to commit), skip straight to Step 3 — there may still be committed-but-unpushed or unreleased work.

## Step 2 — Push

`git push origin main`. If it fails because main is protected, stop and tell the user — do not fall back to a different branch; this repo's own main is the template's source of truth, not a client SOW branch.

## Step 3 — Determine the version bump

1. `CURRENT_TAG=$(git describe --tags --abbrev=0)`.
2. `git log --oneline <CURRENT_TAG>..HEAD` — this now includes whatever just got committed/pushed in Steps 1–2, plus anything already on main since the last release.
3. If that range is empty, tell the user "Already at `<CURRENT_TAG>`, nothing to release" and stop.
4. If a version was passed as an argument, use it directly and skip inference.
5. Otherwise infer from the commit subjects in that range, conventional-commits style:
   - Any subject containing `BREAKING CHANGE` (in the subject or body) → **major**
   - Else any subject starting with `feat` → **minor**
   - Else (`fix`, `chore`, `docs`, `refactor`, anything else) → **patch**
   - Use the single highest-precedence match across all commits in range (major > minor > patch).

## Step 4 — Confirm with the user

Show the commit list from Step 3 and the inferred (or user-supplied) next version, e.g.:

```
Commits since v1.0.1:
  08ab7a5 fix(meeting-summary): align Action Items format with /action-board convention

Inferred bump: patch → v1.0.2
```

Ask: proceed with this version, type a different one, or abort. Do not call `release.sh` before getting this confirmation, even if a version was passed as an argument — the argument skips *inference*, not confirmation.

## Step 5 — Release

Run `.kernel/release.sh <confirmed-version>` non-interactively (pass the version as `$1` so it skips its own bump prompt). It still asks its own `Proceed? [y/N]` — answer `y` since the user already confirmed in Step 4. It commits `.2ndbrain-version`, tags, and pushes both `main` and the tag.

## Step 6 — Report

One line: what was committed (or "nothing to commit"), whether it pushed cleanly, and the version transition (`vOLD → vNEW`). If the user has a `.kernel/template-upgrade-repos.yaml` with target repos configured, remind them: "Run `/template-upgrade-repos` to sync this into client repos."

## Notes

- This command is maintainer tooling for the template repo itself (`ai-project-2ndbrain`) — never run it inside a client repo.
- Never skip Step 4's confirmation, even when a version is supplied as an argument or the bump seems obvious — a pushed tag is hard to walk back.
- If commit message prefixes don't follow conventional-commits at all (mixed styles), say so and ask the user to pick the bump type instead of guessing.
