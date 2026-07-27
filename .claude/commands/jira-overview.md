Produce a fresh Jira ticket overview snapshot for a SOW's team — refreshed status, days-in-status, what's new, and a Slack-ready Executive Summary — without needing to already be working inside that SOW's jira-status session.

## Usage

```
/jira-overview [sow]
```

`sow` is optional — only needed when the vault has more than one SOW with a `work/jira-status/` session set up.

---

## 1 — Resolve the SOW and load its config

- Scan `sows/` for subdirectories excluding `_template`.
- If a SOW name was passed as an argument, use it. If only one SOW has a `work/jira-status/CLAUDE.md`, use it. Otherwise ask which SOW.
- Read `sows/<sow>/work/jira-status/CLAUDE.md` in full. It owns all the instance-specific detail this command needs: which MCP server to use and its auth quirks, the JQL refresh query and who's tracked, the snapshot file location and naming convention, the "closed since last snapshot" diffing logic, and the Executive Summary format. **If that file doesn't exist yet, stop.** Tell the user this SOW hasn't been set up for Jira tracking, and that running `/jira-onboard <sow>` will set it up. Don't try to improvise the config yourself — it depends on client-specific facts (which MCP server, project key, team roster, JQL) that shouldn't be guessed.

## 2 — Get the real current date/time

Run `date +"%Y-%m-%d %H:%M"`. Never assume the current date matches whatever date is embedded in the Jira content being summarized — they can drift.

## 3 — Refresh from Jira

Run the JQL refresh query from `jira-status/CLAUDE.md` against the MCP server it specifies. For anything that looks new or changed since the last snapshot, pull full detail (`comments,changelog`) rather than trusting the `updated` timestamp alone — bulk automation events (sprint carry-over, etc.) can touch `updated` on every ticket without any real change. Check the changelog detail before treating a timestamp as a signal.

Don't trust Jira status alone as ground truth for real readiness — if the working session's notes flag known discrepancies (e.g. a ticket the team has said isn't actually ready despite showing "Review"), carry that forward rather than re-reporting the raw Jira status uncritically.

## 4 — Diff against the last snapshot

Follow the "Closed since last snapshot" procedure in `jira-status/CLAUDE.md` exactly: find the most recent snapshot with an earlier calendar date as the baseline, verify (don't assume) anything that disappeared from the live query, and accumulate same-day closures rather than dropping them between same-day runs.

## 5 — Write the snapshot

Save to the path and filename convention `jira-status/CLAUDE.md` specifies (dated + timed, under that SOW's `ticket-overview/` directory). Structure: `## Executive Summary` (Wins / Needs attention / Next steps, per the format specified in `jira-status/CLAUDE.md`) first, then the full ticket detail table, then a "Closed since last snapshot" section, then any notes worth flagging for next time (e.g. corrections found, new discrepancies, process gotchas).

## 6 — Report

Tell the user where the snapshot was saved, then paste the Executive Summary inline in the response so it's immediately copy-pasteable.
