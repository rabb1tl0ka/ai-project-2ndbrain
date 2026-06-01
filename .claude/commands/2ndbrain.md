Your job is to orient the user and tell them exactly what to do next.

---

## Step 1 — Detect current state

**Check onboarding:**
Read `project.config.yaml`. It's complete if the file exists AND none of the values are still template placeholders (e.g. `{{PROJECT_NAME}}`).

**Check bootstrap:**
Read `project-vault/.bootstrap-state.md`. It's complete if `last_ran` has a real date (not empty).

---

## Step 2 — Print the orientation header

Always print this first:

```
Project 2nd Brain — Command Guide

Two commands set up your brain. Run them once, in order.

  Step 1: /onboard     ← run from the repo root (here)
                         Asks for your project config, replaces vault placeholders, creates SOW directories.

  Step 2: /bootstrap   ← run from inside project-vault/ (separate Claude session)
                         Pulls the SOW doc, meeting notes, and Slack history into the vault.

After setup, use these from inside project-vault/:
  /meeting-recap       ← pick up new meetings since last run
  /bootstrap --sow     ← add a new SOW to an already-bootstrapped brain
```

---

## Step 3 — Print current status and next action

Based on what you found in Step 1, print one of the following blocks:

### State A — Nothing done yet (config missing or has placeholders)

```
Current status:
  ✗  Onboarding not done
  ✗  Bootstrap not done

Next: run /onboard (you're already in the right place)
```

### State B — Onboarded, bootstrap not done

```
Current status:
  ✓  Onboarded — project.config.yaml is set
  ✗  Bootstrap not done

Next:
  cd project-vault
  claude
  Then run /bootstrap
```

### State C — Fully set up

Read `project-vault/.bootstrap-state.md` for `last_ran` and `sows_processed`.
Read `project.config.yaml` for `PROJECT_NAME`, `CLIENT_NAME`, `ENGAGEMENT_TYPE`, `OWNER_NAME`, `OWNER_HANDLE`, `OWNER_ROLE`.

**Per-SOW details:**

For each SOW directory in `project-vault/sows/` (excluding `_template`), in order:

1. Read `project-vault/sows/<sow>/sow.config.yaml`.
2. **One-liner (lazy cache):**
   - If `DESCRIPTION` exists and is non-empty in `sow.config.yaml`, use it.
   - Otherwise: read `project-vault/sows/<sow>/<sow>-reference.md`, summarize the SOW scope in one sentence, then write it back to `sow.config.yaml` by appending `DESCRIPTION: "<summary>"` to the file.
3. Count `.md` files in `project-vault/sows/<sow>/meeting-summaries/` (0 if directory doesn't exist).
4. Check if `project-vault/sows/<sow>/slack-context.md` exists.
5. Read `SLACK_CHANNELS` from `sow.config.yaml` (empty string if not set).
6. Read `NOTION_PROJECT_URL` from `sow.config.yaml` (empty string if not set).

Print:

```
Current status:
  ✓  Onboarded
  ✓  Bootstrapped — last ran <last_ran>

Project: <PROJECT_NAME> — <ENGAGEMENT_TYPE>
Client:  <CLIENT_NAME>
Owner:   <OWNER_NAME> (<OWNER_ROLE>, <OWNER_HANDLE>)

SOWs:
  • <sow> — <DESCRIPTION>
             <N> meeting summaries, slack context ✓/✗
             Slack:   <SLACK_CHANNELS or "(none configured)">
             Notion:  <NOTION_PROJECT_URL or "(none configured)">

  (repeat for each SOW)

Next: cd project-vault && claude, then /meeting-recap to pick up new meetings.
```

---

Do not ask any questions. Do not run any setup. Just orient and point.
