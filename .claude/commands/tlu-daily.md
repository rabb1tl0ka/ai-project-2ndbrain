Generate a Daily TLU for a SOW — a same-day delta report showing what's actually moved since the last time this was checked, meant to be run multiple times a day as a progress pulse-check. Unlike `/tlu` (a weekly status covering the prior calendar week), this always diffs against the last known snapshot, however long ago that was.

## Usage

```
/tlu-daily <sow>
```

`sow` is required — only skip resolving it if there's exactly one SOW in `sows/` (excluding `_template`); otherwise ask which SOW.

---

## 1 — Resolve the SOW

- Scan `sows/` for subdirectories excluding `_template`.
- If a SOW name was passed as an argument, use it.
- If no argument was passed: if only one SOW exists, use it. Otherwise ask which SOW — never guess.

## 2 — Get the real current date/time

Run `date +"%Y-%m-%d %H:%M"`. Never assume — this both dates the output file and decides which snapshot counts as "today's."

## 3 — Find the anchor snapshot

Snapshots live at `sows/<sow>/daily-tlus/.snapshots/YYYY-MM-DD.md`, one per calendar day. Each holds only frontmatter:

```
---
date: YYYY-MM-DD
commit_hash: <git rev-parse HEAD at snapshot time>
run_time: YYYY-MM-DD HH:MM
---
```

- List files in `sows/<sow>/daily-tlus/.snapshots/`. The anchor is the most recent one dated **before today** — if a day (or several) got skipped, that's fine, just use whatever the latest one actually is. Don't special-case gaps.
- **If no snapshot exists at all** (first-ever run for this SOW): there's nothing to diff against. Skip steps 4-6 (no delta, no Jira delta, no momentum marker to judge) but still do step 6a (full task board snapshot) — then go to step 7, write today's snapshot, and tell the user this was a baseline-capture run with no delta to report, and that running it again later will produce the first real comparison.

## 4 — Compute the delta

Using the anchor's `commit_hash`:

```
git diff <commit_hash> -- sows/<sow>
git status --porcelain -- sows/<sow>
```

The `diff` covers committed changes since the anchor; `status --porcelain` catches anything new/uncommitted (nothing needs to be committed for it to show up in the delta — this is a live working-tree comparison, not a commit-to-commit one). Read both together. From this, work out:

- **Tasks added** — new files under `sows/<sow>/tasks/`
- **Tasks closed** — files that moved to `sows/<sow>/tasks/done/` with a `closed:` date in the window
- **Tasks meaningfully updated** — existing task files whose `status`, `priority`, or `## Notes` changed (ignore trivial reformatting)
- **New meeting summaries / working-session activity** — new or changed files under `sows/<sow>/meeting-summaries/` or `sows/<sow>/work/`

Don't invent movement that isn't in the diff — if nothing changed on a given axis, say so plainly rather than padding the report.

## 5 — Get the Jira delta

Look in `sows/<sow>/work/ticket-overview/` for the most recent snapshot file.

- If its timestamp is newer than the anchor's `run_time`, pull its `## Executive Summary` and "Closed since last snapshot" section as the Jira delta for this report.
- If the freshest Jira snapshot is **not** newer than the anchor (or none exists), don't report stale Jira data as current. Say so explicitly, and ask the user whether to run `/jira-overview <sow>` first or proceed without a Jira delta — never run it automatically (same rule `/tlu` follows).

## 6 — Judge the momentum marker

Pick one, based on the actual diff from step 4 and the Jira delta from step 5 — not a mechanical count:

- 📈 **Progress** — things closed, blockers resolved, or real forward movement outweighs anything new getting stuck
- ➡️ **Flat** — no meaningful change either way since the anchor
- 📉 **Regressing** — new blockers surfaced, previously-moving items stalled, or ground was lost with nothing offsetting it

State the reasoning behind the marker in the Notes section — don't leave it as an unexplained emoji.

## 6a — Build the full open task board snapshot

Read every file under `sows/<sow>/tasks/*.md` (excluding `tasks/done/`) and build a compact table (ID, Task, Owner, Priority, Status only — leave out Notes, it's too long for this view) covering **every currently open task**, not just what changed today. This is the "whole radar" view so anyone reading the daily report sees everything in flight, not only the delta.

- Sort: `blocked` status first, then by priority (`high` → `medium` → `low`), then by ID.
- Point to the individual task file under `sows/<sow>/tasks/` for full context/Notes on any item — don't duplicate the Notes section here.
- This section is unconditional — include it even on a first-ever run with no delta to report (see step 3).

## 7 — Fill the template and save

Read `templates/tlu-daily.md` and copy its structure first, fill content second — never write this from scratch. Save to:

```
sows/<sow>/daily-tlus/YYYY-MM-DD-HHMM-tlu-daily.md
```

(one file per run — timestamp comes from step 2).

## 8 — Write today's snapshot

Write/overwrite `sows/<sow>/daily-tlus/.snapshots/YYYY-MM-DD.md` with today's date, `git rev-parse HEAD`, and the current run time. This becomes tomorrow's anchor (or a later day's, if tomorrow gets skipped). Overwriting it on every run today is intentional — the anchor-selection rule in step 3 always excludes today's own file, so re-running later today still diffs against the same prior-day anchor, giving a growing intra-day delta.

## 9 — Report

Tell the user where the file was saved, then paste the "Progress since last check" and "Jira delta" sections inline so they're immediately readable without opening the file.
