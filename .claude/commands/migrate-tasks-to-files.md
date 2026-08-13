One-time migration: convert a SOW's old table-based task board (`sows/<sow>/<sow>-tasks.md` + `sows/<sow>/done/YYYY-WW.md` weekly logs) into the current one-file-per-task format (`sows/<sow>/tasks/<task-id>.md` + `sows/<sow>/tasks/done/<task-id>.md`).

Only needed for SOWs created before the tasks-as-files change. New SOWs created with the current `/onboard` never have a table to migrate.

This is a manual, confirmed step, run once per SOW — never automatic (e.g. not part of `/upgrade`). It rewrites the on-disk shape of live task data, so it always needs a human to review the proposed conversion before anything is written.

## Usage

```
/migrate-tasks-to-files [sow]
```

`sow` is optional — only needed when the vault has more than one SOW.

---

## 1 — Resolve the SOW

- Scan `sows/` for subdirectories excluding `_template`.
- If a SOW name was passed as an argument, use it. If only one SOW exists, use it. Otherwise ask which SOW.

## 2 — Check whether migration is needed

- If `sows/<sow>/<sow>-tasks.md` doesn't exist, report: "No table-based task board found for `<sow>` — nothing to migrate." Stop.
- If it exists but has no data rows (header + separator only), report that it's empty, ask whether to still create the `tasks/` scaffold or skip entirely.

## 3 — Parse the table

Read `sows/<sow>/<sow>-tasks.md`. Find the markdown table (header row, separator row of dashes, then data rows):

- Skip the `|---|---|...` separator row
- For each data row: split on `|`, drop the empty leading/trailing cells from the outer pipes, trim whitespace from each cell
- Map columns positionally to `ID, Task, Owner, Priority, Due, Session, Status, Notes` — don't assume column order matches the header text exactly; read the header row first and map by header name, falling back to position only if a header name doesn't match any expected field
- A cell containing a literal `|` (escaped as part of the table syntax, e.g. `\|`) should be unescaped back to a plain `|` in the resulting file — Notes is the column most likely to contain this
- Empty `Due` stays empty (omit the `due:` field's value, keep the key)

Also read every `sows/<sow>/done/*.md` weekly log file. Each is a table in the same shape, plus a `Closed` date column. Parse the same way.

## 4 — Propose the conversion

Present a summary before writing anything:

```
## Proposed migration for <sow>

Open tasks → sows/<sow>/tasks/ (N files)
- <id>: <task> (owner: <owner>, status: <status>)
- ...

Closed tasks → sows/<sow>/tasks/done/ (M files)
- <id>: <task> (closed: <date>)
- ...

Source files that will be removed after migration:
- sows/<sow>/<sow>-tasks.md
- sows/<sow>/done/*.md (N files)
```

Ask: "Proceed with this migration, adjust, or skip?"

## 5 — Write the task files

On confirmation:

1. Create `sows/<sow>/tasks/` and `sows/<sow>/tasks/done/` if they don't exist.
2. For each open row, write `sows/<sow>/tasks/<id>.md`:

   ```markdown
   ---
   id: <id>
   task: "<task>"
   owner: <owner>
   priority: <priority>
   due: <due or omit value>
   session: <session>
   status: <status>
   ---

   ## Notes

   <notes, or omit the section if empty>
   ```

3. For each closed row (from `done/*.md`), write `sows/<sow>/tasks/done/<id>.md` the same way, plus `closed: <date>` in the frontmatter.
4. If two rows across open/closed sources share the same `id`, the closed one wins (it's the more recent state) — warn about the collision before writing.

## 6 — Remove the old files

Delete `sows/<sow>/<sow>-tasks.md` and every `sows/<sow>/done/*.md` file (leave `sows/<sow>/done/.gitkeep` if present, or remove the now-empty `done/` directory entirely — `tasks/done/` replaces it).

## 7 — Report

```
✓ Migrated <sow>'s task board.
  <N> open task files written to sows/<sow>/tasks/
  <M> closed task files written to sows/<sow>/tasks/done/
  Old table and weekly done logs removed.

Review the new files before committing: git status
```
