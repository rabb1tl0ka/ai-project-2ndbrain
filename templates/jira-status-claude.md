# Jira Status Tracking — {{SOW_NAME}}

## What this is

Working config for pulling the latest Jira status on the tickets assigned to {{TEAM_LIST}} on the {{ENGAGEMENT_NAME}} engagement. Use this whenever the user asks for "the latest Jira status" or "check for updates on our tickets."

## MCP server

Use `{{MCP_SERVER_NAME}}` MCP tools{{OTHER_JIRA_MCP_NOTE}}.

{{AUTH_TROUBLESHOOTING_NOTES}}

## Who we track

{{TEAM_ROSTER}}

## Refresh query

This is the canonical JQL to pull the current list of open-sprint tickets for the team. Ticket IDs churn over time (closed/opened), so don't hardcode a ticket list — always re-run this query first:

```
{{JQL_QUERY}}
```

Run via `mcp__{{MCP_SERVER_NAME}}__jira_search` (or the equivalent search tool for this MCP server) with `fields: "summary,status,assignee,updated,created"`.

For per-ticket news/comments since a given date, follow up with the equivalent `jira_get_issue` tool per key, `include: "comments,changelog"`.

## Project key

{{ENGAGEMENT_NAME}} tickets live under Jira project key **{{PROJECT_KEY}}**.

## How to check "what's new"

1. Run the refresh query above to get the current ticket list + `updated` timestamps.
2. Compare `updated` against the last time this was checked (see "Last checked" below, or ask the user).
3. For any ticket updated since then, pull full detail with `comments,changelog` to see what actually changed (new comment, status transition, reviewer assignment, etc.) — `updated` alone doesn't say what changed. Bulk automation events (sprint carry-over, nightly jobs) can touch `updated` on every ticket with no real change — check changelog detail before treating a timestamp as a signal.
4. Flag specifically: any client-side response (or lack of one) on tickets in Review, new blockers/open questions raised by the team, and any ticket that moved into Review.
5. **Don't trust Jira alone.** Jira status (e.g. "Review") can lag real state — confirm with the team directly before reporting a ticket as ready/blocked/answered. Client responses sometimes happen over Slack/Teams/verbally and never get logged as a Jira comment, so "no new Jira activity" is not proof "no response happened."

## Snapshots

Point-in-time ticket overview tables (title/owner/status/days-in-status/note) are saved as dated snapshots at `sows/{{SOW_NAME}}/work/ticket-overview/ticket-overview-YYYY-MM-DD-HHMM.md` — the time component is required, since this can be requested more than once per day. Get the real current date/time with `date +"%Y-%m-%d %H:%M"` before naming the file — don't assume it matches the date embedded in whatever Jira content you're summarizing (they can drift, e.g. a long session crossing midnight). When asked to "recreate the ticket overview" or produce a fresh table, save the output there rather than just replying inline, so there's a record to diff against next time. Sort rows by days-in-status descending. Keep the `Note` column dedicated to actual notes — put the ticket title in its own column.

### "Closed since last snapshot" section

Every snapshot includes a section listing tickets closed since a baseline, to show progress rather than just a static queue:

1. Find the most recent previous snapshot file in this directory with an **earlier calendar date** than today (not just the immediately prior snapshot). That's the baseline.
2. Compare today's live ticket list against that baseline's active tickets. Anything present there but missing from today's fresh query needs to be individually checked — never assume "disappeared from the query" means "Done." It could mean reassigned, pulled from the sprint, or moved to another board. Only report it as closed once confirmed.
3. The closed section accumulates across same-day snapshots: if this isn't the first snapshot of the day, don't drop items already reported closed earlier today — keep them, and add anything newly closed since. Re-verify each one's current status at snapshot time before repeating it (a ticket can be reopened; don't carry forward a stale "closed" claim unchecked).
4. Once a new calendar day starts, the closed section resets — only that day's own closures show, not the previous day's.

### Executive Summary section

Every snapshot opens with an `## Executive Summary`, written so it can be copy-pasted straight into Slack with no further editing. Three subsections, always in this order:

- **Wins:** tickets closed since the last snapshot (see "Closed since last snapshot" logic above) — one line each, with days-in-prior-status and who actually drove it closed.
- **Needs attention:** start with a single line listing every ticket genuinely waiting on client review, with days-in-status in parens — e.g. "These tickets are waiting on client review: PDI-X (3 days), PDI-Y (7 days)". **Exclude any ticket showing "Review" in Jira that the team has said isn't actually ready** (that's a hygiene problem, not a review-wait — it goes in Next steps instead). Follow with other risks/blockers worth flagging: partial/off-Jira responses awaiting follow-up, scheduling conflicts, anything blocking without a committed resolution date.
- **Next steps:** concrete actions — status corrections needed, reschedules needed, anything with a clear owner.

Keep internal-only risks out of this section unless told otherwise — this summary is written assuming it may be shared externally.

## Last checked

- Not yet run.
