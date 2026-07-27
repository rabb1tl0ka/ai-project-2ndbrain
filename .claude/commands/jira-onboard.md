Set up Jira status tracking for a SOW that doesn't have one yet — the config `/jira-overview` depends on. Run this once per SOW before `/jira-overview` will work for it.

## Usage

```
/jira-onboard [sow]
```

`sow` is optional — only needed when the vault has more than one SOW.

---

## 1 — Resolve the SOW

- Scan `sows/` for subdirectories excluding `_template`.
- If a SOW name was passed as an argument, use it. If only one SOW exists, use it. Otherwise ask which SOW.
- Check `sows/<sow>/work/jira-status/CLAUDE.md`. If it already exists, tell the user it's already set up, show them the current config, and ask if they want to reconfigure before overwriting anything.

## 2 — Gather what's SOW/client-specific

Ask the user directly — don't guess any of this, it's client- and engagement-specific:

1. **Which Jira MCP server to use.** Use `ToolSearch` with a query like "jira" to see what's connected in this session, and show the user the matches so they can pick (there may be more than one Jira MCP connected for different clients/projects — picking the wrong one silently would query the wrong Jira instance).
2. **Jira project key** (e.g. `PDI`) — the ticket prefix for this engagement.
3. **Team roster** — names and emails of who to track. Note that a person's Jira display name can differ from the name used in client-facing docs (same account, different surname convention, etc.) — ask the user to flag if they already know of such a mismatch, so it doesn't need rediscovering later.
4. **JQL query** — offer to construct a default (`project = <KEY> AND sprint in openSprints() AND assignee in (<roster>) ORDER BY assignee, status`) and confirm it with the user rather than assuming it's right — some engagements may not use sprints, may need a different status filter, etc.
5. **Any known MCP auth quirks** for this server (e.g. token setup via a gitignored `private/*.env` + direnv, known gotchas). If the user doesn't know of any yet, leave this section as a placeholder to fill in later rather than inventing one.

## 3 — Generate the config

Read `templates/jira-status-claude.md`. Fill in the placeholders with what was gathered in step 2. Write the result to `sows/<sow>/work/jira-status/CLAUDE.md`.

## 4 — Set up the working session and snapshot directory

Following this repo's working-session convention (see the root `CLAUDE.md`):
- Create `sows/<sow>/work/jira-status/jira-status.md` from `templates/working-session.md`, titled "Jira Status Tracking," with a one-sentence "What this is" tying it to keeping Jira as the source of truth for the team's ticket status.
- Create `sows/<sow>/work/ticket-overview/` (empty — the first `/jira-overview` run will populate it).
- Add a row for `jira-status` to the `## Active Working Sessions` table in `sows/<sow>/<sow>-reference.md`.

## 5 — Report

Confirm what was created and where. Tell the user `/jira-overview <sow>` is now ready to run.
