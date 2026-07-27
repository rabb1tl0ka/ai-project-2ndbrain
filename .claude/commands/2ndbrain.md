Your job is to orient the user and tell them exactly what to do next.

---

## Step 1 — Detect current state

**Check onboarding:**
Read `config.yaml`. It's complete if the file exists AND none of the values are still template defaults (e.g. `"Your Client Inc."`).

**Check bootstrap:**
Read `.bootstrap-state.md`. It's complete if `last_ran` has a real date (not empty).

---

## Step 2 — Print the orientation header

Always print this first:

```
Engagement Brain — Command Guide

Two commands set up your brain. Run them once, in order.

  Step 1: /onboard     ← run once from this directory
                         Asks for client name, owner info, SOW list.
                         Replaces vault placeholders, creates SOW directories.

  Step 2: /bootstrap   ← run after /onboard (same session is fine)
                         Pulls the SOW doc, meeting notes, Slack, and Notion
                         history into the vault.

After setup, use these ongoing:
  /meeting-recap       ← pick up new meetings via Calendar since last run
  /meeting-recap-drive ← same, but via a Drive folder (backfill / pre-brain history)
  /bootstrap --sow     ← add a new SOW to an already-bootstrapped brain
```

---

## Step 3 — Print current status and next action

Based on what you found in Step 1, print one of the following blocks:

### State A — Nothing done yet (config missing or has placeholder defaults)

```
Current status:
  ✗  Onboarding not done
  ✗  Bootstrap not done

Next: run /onboard (you're already in the right place)
```

### State B — Onboarded, bootstrap not done

```
Current status:
  ✓  Onboarded — config.yaml is set
  ✗  Bootstrap not done

Next: run /bootstrap
```

### State C — Fully set up

Read `.bootstrap-state.md` for `last_ran` and `sows_processed`.
Read `config.yaml` for `CLIENT_NAME`, `OWNER_NAME`, `OWNER_ROLE`.

**Version check (silent on failure):**

Read `.kernel/.2ndbrain-version` for the current version. Then run:
```bash
git ls-remote --tags https://github.com/rabb1tl0ka/ai-project-2ndbrain 2>/dev/null \
  | grep -o 'refs/tags/v[0-9]*\.[0-9]*\.[0-9]*' | sort -V | tail -1 | grep -o 'v.*'
```
If this fails for any reason (no network, timeout), skip silently — do not block the output.
Compare the latest tag to the current version. Store result as `UPDATE_AVAILABLE` (true/false).

**Per-SOW details:**

For each SOW directory in `sows/` (excluding `_template`), in order:

1. Read `sows/<sow>/sow.config.yaml`.
2. **One-liner (lazy cache):**
   - If `DESCRIPTION` exists and is non-empty in `sow.config.yaml`, use it.
   - Otherwise: read `sows/<sow>/<sow>-reference.md`, summarize the SOW scope in one sentence, then write it back to `sow.config.yaml` by appending `DESCRIPTION: "<summary>"`.
3. Count `.md` files in `sows/<sow>/meeting-summaries/` (0 if directory doesn't exist).
4. Check if `sows/<sow>/slack-context.md` exists.
5. Read `SLACK_CHANNELS` from `sow.config.yaml` (empty string if not set).
6. Read `NOTION_PROJECT_URL` from `sow.config.yaml` (empty string if not set).
7. Check if the SOW branch exists on remote:
   ```bash
   git ls-remote --heads origin <sow>
   ```
   Store as `BRANCH_EXISTS` (true if output is non-empty, false otherwise).

Print:

```
Current status:
  ✓  Onboarded
  ✓  Bootstrapped — last ran <last_ran>

Engagement Brain — <CLIENT_NAME>
Owner:   <OWNER_NAME> (<OWNER_ROLE>)

SOWs:
  • <sow> — <DESCRIPTION>
             <N> meeting summaries, slack context ✓/✗
             Branch:  origin/<sow> ✓  (or "✗ — run /bootstrap --sow <sow> to create it")
             Slack:   <SLACK_CHANNELS or "(none configured)">
             Notion:  <NOTION_PROJECT_URL or "(none configured)">

  (repeat for each SOW)

Next: /meeting-recap to pick up new meetings.
```

If `UPDATE_AVAILABLE` is true, append:

```
⚠  Update available: <current_version> → <latest_version>
   Run /upgrade to see what changed, /upgrade --apply to update.
```

---

Do not ask any questions. Do not run any setup. Just orient and point.
