Publish a vault markdown file to Notion as a child page of this SOW's project page.

## Usage

```
/publish-to-notion <relative-path-to-file>
```

Example: `/publish-to-notion sows/sow1/deliverables/architecture-overview.md`

---

## Pre-flight

### 1 — Check Notion connector

Attempt to list Notion tools. If the Notion MCP connector is not available, print:

> "⚠ Notion connector not found. To use this command, enable the Notion connector in your Claude settings (claude.ai → Integrations → Notion), then restart your session."

Stop here. Do not throw an error — just warn and exit.

### 2 — Resolve the SOW

From the file path, infer which SOW this file belongs to (the `sows/<sow>/` segment). If the file is not inside a SOW directory, ask:

> "Which SOW does this file belong to? (e.g. sow1, sow2)"

### 3 — Read SOW config

Read `sows/<sow>/sow.config.yaml`. Extract `NOTION_PROJECT_URL`.

If `NOTION_PROJECT_URL` is empty, print:

> "⚠ No Notion project URL configured for <sow>. Add it to sows/<sow>/sow.config.yaml:
>
>     NOTION_PROJECT_URL: "https://www.notion.so/..."
>
> Then re-run this command."

Stop here.

---

## Publish

### 1 — Derive the page title

Use the filename without the `.md` extension as the Notion page title.
Example: `architecture-overview.md` → title `architecture-overview`

### 2 — Search for an existing page

Using the Notion MCP, search for child pages of `NOTION_PROJECT_URL` whose title exactly matches the derived title.

- If a match is found: **update** that page with the new content.
- If no match is found: **create** a new child page under `NOTION_PROJECT_URL`.

### 3 — Convert and push content

Read the file. Push its content to Notion as the page body. Preserve heading levels, bullet lists, and code blocks where the Notion API allows.

### 4 — Report result

Print one of:

```
✓ Updated Notion page "<title>"
  <notion-page-url>
```

```
✓ Created Notion page "<title>"
  <notion-page-url>
```

If the push fails, print the error plainly and suggest checking that the Notion connector has edit access to the target page.
