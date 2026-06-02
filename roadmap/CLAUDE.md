# Roadmap Convention

This repo uses a `roadmap/` directory to track features, ideas, and challenges for the engagement.

## Directory structure

```
roadmap/
  feat-name/              ← workspace item (spec + supporting material)
    feat-name.md
    docs/
  idea-simple.md          ← flat item (no workspace needed)
  archived/               ← completed or abandoned items (omitted from table)
  templates/
  README.md
  CLAUDE.md
```

Every roadmap entry is either:
- A **flat `.md` file** — simple items with no supporting material
- A **workspace directory** — items with a spec file + `docs/` for research, references, and artifacts

## File naming

Every roadmap entry uses one of three prefixes:
- `feat-` — fully specced feature, ready to implement
- `idea-` — early exploration, not yet fully designed
- `challenge-` — known problem, solution still open

## Reviewing specs

Use `[YourName: your comment]` to annotate specs inline. Claude Code will recognize these as reviewer comments when asked to review them.

## Roadmap Management Rules (Strict - Always Follow)

You are the active maintainer of the roadmap in the `roadmap/` directory.

### Frontmatter (minimal)
Every roadmap file must start with this exact frontmatter block:

---
status: todo | in-progress | done | blocked | review | rejected
priority: high | medium | low
owner: ""
phase: ""
depends_on: []
---

When a roadmap item is published to Notion, add `notion_url` to the frontmatter:

---
status: done
priority: medium
owner: ""
phase: ""
depends_on: []
notion_url: "https://www.notion.so/<page-id>"
---

- Default new items to `status: todo`, `priority: medium`, `owner: ""`, `phase: ""`, `depends_on: []`
- When someone picks up an item, set `status: in-progress` and `owner: <handle>`
- Update `status`, `priority`, `owner`, `phase`, and `depends_on` whenever the state changes
- Never remove the frontmatter once added

### Phase

`phase` is an optional label that groups items into a high-level timeline. Examples: `"sow1"`, `"sow2"`, `"mvp"`. Leave empty (`""`) if unassigned.

- Items in the same phase ship together — phase is a grouping, not a strict gate
- Sort items in the table by phase first (numeric phases first, unassigned last)
- Leave empty by default — only set when the user specifies a phase

### Dependencies

`depends_on` is a list of slugs this item should not be started before.

- Slugs must match the filename prefix of the target item
- When a user picks up an item, check `depends_on` and warn if any dependency is not `done`
- When generating the table, resolve each slug to a markdown link

### Status values

| Status | Emoji | Meaning |
|--------|-------|---------|
| `todo` | ⏳ | Not started |
| `in-progress` | 🚧 | Actively being worked on |
| `done` | ✅ | Complete |
| `review` | 🔍 | Ready for review |
| `blocked` | ❌ | Cannot proceed — external impediment |
| `rejected` | 🚫 | Deliberate decision not to pursue |

**blocked vs rejected:**
- `blocked` = something outside our control is holding it back; may become unblocked
- `rejected` = a conscious decision was made not to pursue this, at least for now

**When marking an item `rejected`:**
1. Add a `## Why this was rejected` section to the spec
2. Update `status: rejected` and refresh the table
3. Do NOT archive rejected items — keep them visible so the decision is on record

### One-Line Overview
Every file must have a `## One-Line Overview` section right after the main title.
- One single, crisp sentence
- Describes the problem-solution space, not just the goal
- Used for the overview table

### When asked to save a feature, idea, or challenge

1. Use the matching template from `roadmap/templates/`
2. Create as a workspace directory:
   - `mkdir roadmap/<prefix>-<slug>/`
   - Create `roadmap/<prefix>-<slug>/<prefix>-<slug>.md` from the template
   - Create `roadmap/<prefix>-<slug>/docs/`
3. Add a row to the `## Current roadmap` table in `roadmap/README.md`

### Promotion (flat → workspace)

When a user asks to create a `docs/` directory for a flat item:
1. Create `roadmap/<prefix>-<slug>/` directory
2. Move `roadmap/<prefix>-<slug>.md` into it
3. Create `roadmap/<prefix>-<slug>/docs/`
4. Update the table link

### When asked to archive an item

1. Update `status: done` in the spec file
2. Move the entire item (file or directory) to `roadmap/archived/`
3. Remove from the active table in `roadmap/README.md`

### Automatic Table Maintenance

After **any** of the following, regenerate the entire "Current roadmap" table in `roadmap/README.md`:
- Creating a new roadmap entry
- Updating status, priority, phase, depends_on, or One-Line Overview
- Archiving, deleting, or renaming an item

**How to generate the table:**
1. Scan `roadmap/` for entries matching `feat-*`, `idea-*`, `challenge-*`
   - `.md` file → parse directly
   - Directory → look for `<dirname>.md` inside it
   - Skip anything inside `roadmap/archived/`
2. Parse frontmatter for status, priority, phase, depends_on
3. Extract the `## One-Line Overview` text
4. Build the markdown table with columns: File, Phase, Status, Priority, Deps, Owner, One-Line Overview
5. Sort by: phase (numeric ascending, unassigned last), then type (feat → idea → challenge), then priority (high → medium → low), then filename
6. Place under `## Current roadmap`. Keep the note: "(The table above is automatically maintained by Claude Code. Do not edit it manually.)"

### Useful Commands

- "Update roadmap table" → Regenerate the full table
- "Show roadmap" → Print a formatted summary grouped by type
- "Mark [item] as done/in-progress/blocked" → Update frontmatter + refresh table
- "Set priority of [item] to high/medium/low" → Update + refresh table
- "Set phase of [item] to [phase]" → Update `phase` frontmatter + refresh table
- "Pick [item]" → Set `status: in-progress` + `owner: <handle>` + check depends_on + refresh table
- "Archive [item]" → Mark done, move to `roadmap/archived/`, remove from table
- "Reject [item]" → Prompt for rationale, add `## Why this was rejected`, set `status: rejected`, refresh table
