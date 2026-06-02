Pull the latest content from this SOW's Notion project page and update notion-context.md.

## Usage

```
/fetch-from-notion [sow-name]
```

If `sow-name` is omitted, infer it from the current working directory or ask.

---

## Pre-flight

### 1 — Check Notion connector

Attempt to list Notion tools. If the Notion MCP connector is not available, print:

> "⚠ Notion connector not found. Enable it in Claude settings (claude.ai → Integrations → Notion) and restart your session."

Stop here.

### 2 — Resolve the SOW

If `sow-name` was passed, use it. Otherwise check the current directory path for a `sows/<name>/` segment. If still unclear, ask:

> "Which SOW should I fetch Notion context for? (e.g. sow1, sow2)"

### 3 — Read SOW config

Read `sows/<sow>/sow.config.yaml`. Extract `NOTION_PROJECT_URL`.

If empty or not set, ask:

> "No Notion project URL configured for [sow]. Paste it to continue, or press enter to cancel."

- If they paste a URL: write it back to `sows/<sow>/sow.config.yaml` as `NOTION_PROJECT_URL: "<url>"`, then continue.
- If they press enter: stop.

---

## Fetch

### 1 — List child pages

Using the Notion MCP, list all child pages of `NOTION_PROJECT_URL`.

If none found:
> "No child pages found under the Notion project page for [sow]. Nothing to fetch."

Stop.

### 2 — Read each child page

For each child page, read its full content. Note its title and any relational properties (especially fields named "Previous Update", "Previous", or similar back-link fields).

### 3 — Traverse TLU chains

After reading all direct child pages, look for any that appear to be TLU (Traffic Light Update) entries — typically identified by date-based titles (e.g. "Jun 01", "May 25") or a "Traffic Light" / "Status" property.

For each TLU page found:
1. Check for a "Previous Update" relational property (or equivalent back-link field).
2. If it points to another page, fetch that page.
3. Repeat until the chain ends (no further "Previous Update" link or the page is empty).
4. Collect all TLU pages in chronological order (oldest → newest).

Read the full content of each TLU page in the chain. Skip pages that are empty but note they exist.

### 4 — Write notion-context.md

Synthesize everything — direct child pages + full TLU chain — into `sows/<sow>/notion-context.md`, overwriting any previous version:

```markdown
---
last_updated: YYYY-MM-DD
source: <NOTION_PROJECT_URL>
---

# Notion Context — <sow>

## Summary
(2-3 sentences: what's published here, what it tells us about project status or decisions)

## Pages found
| Title | Last edited | Key content |
|-------|-------------|-------------|

## TLU History
(TLU entries in reverse chronological order — most recent first)

| Date | Status | Key updates | Blockers |
|------|--------|-------------|----------|

## Key information extracted
-

## ⚠ Flags
(anything worth surfacing: unapproved SOWs, missing TLUs, compliance gaps, access limitations)
```

### 5 — Report

```
✓ Notion context updated → sows/<sow>/notion-context.md
  N pages read (M direct + K TLU entries)
```
