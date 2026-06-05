---
status: todo
priority: medium
owner: ""
phase: ""
depends_on: []
---

# Feature: TLU Generation per SOW

## One-Line Overview
Every SOW gets a `TLUs/` output folder and a `templates/tlu-template.md`, with CLAUDE.md instructions that tell Claude how to generate a weekly Traffic Light Update for the Sales Lead from the SOW's working notes and meeting summaries.

## What's the idea

TLUs (Traffic Light Updates) are weekly executive status emails for the Sales Lead. They cover achievements, blockers (with CTAs + due dates), risks (with mitigations), and anything the Sales Lead needs to manage the AWS or client relationship that week.

Right now the TLU template and generation instructions live in the project-level `CLAUDE.md` — they were written inline for ZenQMS SOW4. This feature moves that pattern into the template so every new SOW gets it automatically at bootstrap.

### What gets scaffolded per SOW

When bootstrap creates a new SOW (e.g. `sows/acme-sow1/`), it should also create:

```
sows/acme-sow1/
  TLUs/                    ← output directory, gitignored from main
  templates/
    tlu-template.md        ← filled with SOW-specific placeholders
```

And the SOW's `CLAUDE.md` (or the root `CLAUDE.md` if project-wide) gets a **TLU section** with:
- Trigger phrases (`"generate a TLU"`, `"generate this week's TLU"`)
- Generation logic (what to read, what to fill)
- Naming convention (`YYYY-MM-DD-tlu.md` — the Monday date)
- Status color rules (Green / Yellow / Red)
- Audience framing (Sales Lead: executive, risks + status, no jargon)

### TLU template structure

The `tlu-template.md` should cover:

1. **Header**: SOW name, week ending date, status color + label
2. **Achievements this week**: bullet list — what shipped, what was resolved
3. **Blockers**: each with owner, CTA, and due date
4. **Risks**: each with mitigation and due date
5. **Notes for [Sales Lead name]**: anything for the client or AWS relationship that week
6. **Next week**: what's coming up

Placeholders (e.g. `{{sow_name}}`, `{{sales_lead}}`) should be filled at bootstrap time and baked into the per-SOW copy.

### Generation logic (what Claude does when triggered)

1. Read all meeting summaries under `sows/<sow>/meeting-summaries/`
2. Read all working session notes under `sows/<sow>/work/` (frontmatter + body)
3. Read the SOW `CLAUDE.md` for current blockers and key decisions
4. Synthesize into the TLU template — no jargon, executive frame, CTA on every blocker
5. Save to `sows/<sow>/TLUs/YYYY-MM-DD-tlu.md` where the date is the Monday of that week

### Where the instructions live

TLU generation instructions go in the **root `CLAUDE.md`**, not `SOW{N}/CLAUDE.md`. Reason: they apply at the project level, and the root CLAUDE.md is the entry point Claude reads first. A section like `## TLUs` with trigger phrases and generation steps — exactly like the ZenQMS pattern.

The per-SOW `tlu-template.md` is the *format artifact*; the root `CLAUDE.md` section is the *behavioral instruction*.

## Expected advantages / benefits

- Every new project gets TLU capability out of the box — no copy-paste from ZenQMS
- Sales Lead always has a consistent weekly touchpoint format regardless of the project
- Forces Claude to synthesize across meeting summaries + working sessions — catches drift between what the team is doing and what the client knows
- Template placeholders make the Sales Lead's name and SOW context visible from day one
- Output goes to a dedicated `TLUs/` folder — easy to find, attach, or audit

## Downsides / risks

- Template needs enough flexibility to work for different project types (MAP Assess, staff aug, fixed SOW) — may need variants or optional sections
- "Monday of that week" convention is rigid — some teams prefer "week ending Friday"; template should document the convention so it's not a surprise
- If the SOW has no meeting summaries yet (week 1), Claude needs a graceful fallback — don't fail, generate a minimal TLU from what's available

## What's been tried already

TLU pattern was designed and used live in ZenQMS SOW4. The instructions lived in `CLAUDE.md` at the root of that project repo (not in `SOW4/CLAUDE.md`). That's the pattern to replicate here as a first-class template feature.

## Implementation steps

1. Add `TLUs/` to the bootstrap SOW directory scaffold
2. Add `templates/tlu-template.md` to the bootstrap SOW directory scaffold, with `{{sow_name}}` and `{{sales_lead}}` placeholders
3. Add a `## TLUs (Traffic Light Updates)` section to the root `CLAUDE.md` template
4. Add `TLUs/` to `.gitignore` patterns (outputs, not source)
5. Update `setup.sh` or bootstrap script to create the above on new SOW init
