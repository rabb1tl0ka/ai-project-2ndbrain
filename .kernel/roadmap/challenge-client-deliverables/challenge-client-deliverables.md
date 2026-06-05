---
status: todo
priority: high
owner: ""
phase: ""
depends_on: []
---

# Challenge: Client Deliverables Boundary

## One-Line Overview

Without a clear structural boundary between internal working files and client-facing outputs, any file in a working session directory is one accidental attachment away from a client.

## What's the problem

Working sessions under `work/<slug>/` accumulate internal content alongside deliverable content: raw discovery notes, internal strategy framing, commercial reasoning, team deliberations, hypotheses that didn't survive review. These files are meant to stay internal.

In practice, the deliverable files (PDFs or polished markdown) live in the same directory tree as the internal files. When it's time to send something to a client, the person preparing the package has to manually identify which files are safe to share. That's a human judgment call made at the worst possible moment — under time pressure, right before a meeting or a Slack message.

**Near-miss that surfaced this risk:** On a consulting engagement, a team prepared multiple deliverable PDFs alongside an internal working notes document. The working notes contained discovery session findings, commercial framing, and internal deliberations. All files ended up in the same output folder. When the time came to send files to the client, the right files were picked — but only by recognition, not by any structural safeguard. There was nothing stopping someone from grabbing the whole folder. The files were right there. It would have been a one-second mistake.

## Why it matters

Internal working files routinely contain:
- **Commercial strategy**: framing of findings designed to generate follow-on work, discussion of what gaps "strengthen the pitch"
- **Internal deliberations**: team debates, disagreements, things that were considered and rejected
- **Unverified hypotheses**: claims or concerns that didn't survive review and weren't meant to be stated to the client
- **Partner-confidential context**: third-party knowledge, prior engagement context, or client assessments that weren't meant to be shared

A client receiving any of these loses trust in the engagement's objectivity, gains leverage in commercial negotiations, and — in the worst case — has grounds to question the integrity of the recommendations they paid for.

## Constraints

Any solution must:
- Make it structurally impossible (or at least structurally obvious) to accidentally include internal files in a client delivery
- Work within the existing `work/<slug>/` working session model
- Not add friction to the working session creation flow
- Be enforceable via CLAUDE.md instructions (so Claude can help enforce it, not just the human)

Any solution must not:
- Require manually maintaining a "safe to share" list (too fragile, forgotten under pressure)
- Scatter deliverables across multiple locations (makes package assembly harder, not easier)

## Approaches considered

| Approach | Status | Why ruled out / still open |
|---|---|---|
| **Deliverables subfolder per working session** (`work/<slug>/deliverables/`) | Open | Keeps deliverables co-located with the work that produced them. But requires per-session discipline to put files in the right place, and the instruction "only share files in `deliverables/`" has to be remembered per session. Still fragile if someone grabs from the parent dir. |
| **Single `deliverables/` directory at the SOW level** (`sow{N}/deliverables/`) | Open — preferred | One canonical location for everything client-facing. Instructions become unambiguous: "only files in `sow{N}/deliverables/` go to the client, full stop." Nothing else is client-facing regardless of how polished it looks. Less fragile because the rule doesn't depend on per-session behavior — it's a single structural invariant. Tradeoff: deliverables are physically separated from the working session that produced them. |
| **Naming convention only** (e.g., `-deliverable` suffix) | Ruled out | Relies entirely on discipline at file creation time. No structural enforcement. Easy to miss. Doesn't prevent someone from grabbing a folder and sending everything. |

## Open questions

1. Should the SOW-level `deliverables/` directory hold final PDFs only, or also the source markdown that generated them?
2. Should CLAUDE.md include an explicit rule: "when preparing files for client delivery, only reference files under `sow{N}/deliverables/` — flag anything else as internal"?
3. How do we handle working sessions that produce intermediate artifacts (e.g., a diagram) that feed a deliverable but aren't deliverables themselves — do those stay in `work/<slug>/` or get promoted?
4. Does the PDF generation step (`html-to-pdf` skill) become the natural "promotion" gate — i.e., generating a PDF means the file is ready to move to `deliverables/`?
