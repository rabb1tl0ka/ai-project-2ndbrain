Generate this week's Traffic Light Update (TLU) for a SOW — a weekly status update for the Sales Lead or engagement sponsor, covering the previous week.

## Usage

```
/tlu <sow>
```

`sow` is required — only skip resolving it if there's exactly one SOW in `sows/` (excluding `_template`); otherwise ask which SOW.

---

## 1 — Resolve the SOW

- Scan `sows/` for subdirectories excluding `_template`.
- If a SOW name was passed as an argument, use it.
- If no argument was passed: if only one SOW exists, use it. Otherwise ask which SOW — never guess between `sow-ods`, `sow3`, etc.

## 2 — Get the real current date

Run `date +"%Y-%m-%d"`. TLUs cover the previous calendar week; the output filename is dated to the Monday of that week. Verify that date actually falls on a Monday with `date -d "<date>" +%A` before using it in the filename or inside the document — never assume.

## 3 — Start from the template

Read `templates/tlu.md` and copy its structure into the new file first. Fill content second. Never write a TLU from scratch.

## 4 — Gather sources

Read all meeting summaries and working session notes under `sows/<sow>/` for the reporting week, plus `sows/<sow>/sow-context.md` for current scope, deliverables, and known blockers.

## 5 — Check for a ticket-overview snapshot

Look in `sows/<sow>/work/ticket-overview/` for a snapshot dated within the week being reported.

- If one exists, use it as the Jira-status source alongside the meeting/session notes.
- If none exists (this should be rare — a normal week should have one), **stop and ask** the user whether to run `/jira-overview <sow>` first or proceed without Jira-derived content. Never run `/jira-overview` automatically.

## 6 — Fill in the content

Achievements, blockers (each with a CTA + due date), risks (each with a mitigation), key notes — pulled from the sources above, not invented. Apply standing drafting conventions (no em-dashes, "workaround" not "stopgap", owner = whoever can close the item).

## 7 — Save and report

Save to `sows/<sow>/TLUs/YYYY-MM-DD-tlu.md` (Monday of the reporting week). Tell the user where it was saved.
