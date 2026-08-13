#!/usr/bin/env python3
"""
ai-project-2ndbrain template test suite.

Tests the mechanics that /onboard, /bootstrap, and /2ndbrain depend on.

Usage:
    python3 .kernel/test.py
"""

import subprocess
import sys
import tempfile
from pathlib import Path

PASS = "\033[32m✓\033[0m"
FAIL = "\033[31m✗\033[0m"

passed = 0
failed = 0


def ok(name):
    global passed
    passed += 1
    print(f"  {PASS}  {name}")


def fail(name, reason=""):
    global failed
    failed += 1
    msg = f"  {FAIL}  {name}"
    if reason:
        msg += f"\n       {reason}"
    print(msg)


def section(title):
    print(f"\n{title}")
    print("-" * len(title))


# ─── Repo structure ───────────────────────────────────────────────────────────

def test_repo_structure():
    section("Repo structure")
    repo = Path(__file__).parent.parent

    dirs = [
        "inbox", "archive", "notes", "templates",
        "stakeholders", "team",
        "sows/_template",
        "sows/_template/meeting-summaries",
        "sows/_template/deliverables",
        "sows/_template/work",
        "sows/_template/tasks",
        "sows/_template/tasks/done",
        ".claude/commands",
        ".kernel",
    ]
    for d in dirs:
        if (repo / d).is_dir():
            ok(f"{d}/ exists")
        else:
            fail(f"{d}/ exists")

    files = [
        "CLAUDE.md",
        "README.md",
        "config.example.yaml",
        ".gitignore",
        "templates/meeting-summary.md",
        "templates/tlu.md",
        "templates/working-session.md",
        "sows/_template/sow.config.yaml",
        "sows/_template/sow-reference.md",
        "sows/_template/tasks/.gitkeep",
        "sows/_template/tasks/done/.gitkeep",
        "sows/_template/CLAUDE.md",
        ".claude/commands/onboard.md",
        ".claude/commands/bootstrap.md",
        ".claude/commands/2ndbrain.md",
        ".claude/commands/meeting-recap.md",
        ".claude/commands/migrate-tasks-to-files.md",
        ".kernel/roadmap/README.md",
    ]
    for f in files:
        if (repo / f).is_file():
            ok(f"{f} exists")
        else:
            fail(f"{f} exists")


# ─── Gitignore ────────────────────────────────────────────────────────────────

def test_gitignore():
    section("Gitignore")
    repo = Path(__file__).parent.parent
    content = (repo / ".gitignore").read_text()

    if ".meeting-recap-state.md" in content:
        ok(".meeting-recap-state.md is gitignored")
    else:
        fail(".meeting-recap-state.md is gitignored")

    if ".obsidian/" in content:
        ok(".obsidian/ is gitignored")
    else:
        fail(".obsidian/ is gitignored")


# ─── config.example.yaml ─────────────────────────────────────────────────────

def test_config_example():
    section("config.example.yaml")
    repo = Path(__file__).parent.parent
    content = (repo / "config.example.yaml").read_text()

    for field in ["CLIENT_NAME", "OWNER_NAME", "OWNER_ROLE"]:
        if field in content:
            ok(f"{field} present")
        else:
            fail(f"{field} present")


# ─── sow.config.yaml template ─────────────────────────────────────────────────

def test_sow_task_board():
    section("SOW task board template files")
    repo = Path(__file__).parent.parent

    if (repo / "sows/_template/CLAUDE.md").is_file():
        ok("sows/_template/CLAUDE.md exists")
    else:
        fail("sows/_template/CLAUDE.md exists")

    if not (repo / "sows/_template/sow-tasks.md").exists():
        ok("sows/_template/sow-tasks.md removed from scaffold")
    else:
        fail("sows/_template/sow-tasks.md removed from scaffold")

    if not (repo / "sows/_template/done").exists():
        ok("sows/_template/done/ (weekly log dir) removed from scaffold")
    else:
        fail("sows/_template/done/ (weekly log dir) removed from scaffold")

    for f in ["sows/_template/tasks/.gitkeep", "sows/_template/tasks/done/.gitkeep"]:
        if (repo / f).is_file():
            ok(f"{f} exists")
        else:
            fail(f"{f} exists")

    claude_content = (repo / "sows/_template/CLAUDE.md").read_text()
    if "{{SOW_NAME}}" in claude_content:
        ok("sows/_template/CLAUDE.md has {{SOW_NAME}} placeholder")
    else:
        fail("sows/_template/CLAUDE.md has {{SOW_NAME}} placeholder")

    if "priority" in claude_content.lower():
        ok("sows/_template/CLAUDE.md references priority inference")
    else:
        fail("sows/_template/CLAUDE.md references priority inference")

    for field in ["id", "owner", "priority", "due", "session", "status"]:
        if field in claude_content:
            ok(f"sows/_template/CLAUDE.md task schema documents '{field}'")
        else:
            fail(f"sows/_template/CLAUDE.md task schema documents '{field}'")

    if "tasks/<task-id>.md" in claude_content and "tasks/done" in claude_content:
        ok("sows/_template/CLAUDE.md documents per-task files under tasks/ and tasks/done/")
    else:
        fail("sows/_template/CLAUDE.md documents per-task files under tasks/ and tasks/done/")

    onboard = (repo / ".claude/commands/onboard.md").read_text()
    if "sow-tasks.md" not in onboard:
        ok("/onboard no longer renames sow-tasks.md")
    else:
        fail("/onboard no longer renames sow-tasks.md")

    if "{{SOW_NAME}}" in onboard and "sed" in onboard:
        ok("/onboard replaces {{SOW_NAME}} placeholder")
    else:
        fail("/onboard replaces {{SOW_NAME}} placeholder")

    root_claude = (repo / "CLAUDE.md").read_text()
    if "sows/<sow>/CLAUDE.md" in root_claude:
        ok("root CLAUDE.md references per-SOW CLAUDE.md")
    else:
        fail("root CLAUDE.md references per-SOW CLAUDE.md")

    if "sows/<sow>/tasks/*.md" in root_claude or "tasks/*.md" in root_claude:
        ok("root CLAUDE.md's task board sync section points at tasks/*.md, not a table file")
    else:
        fail("root CLAUDE.md's task board sync section points at tasks/*.md, not a table file")


def test_migrate_tasks_command():
    section("/migrate-tasks-to-files")
    repo = Path(__file__).parent.parent

    skill_path = repo / ".claude/commands/migrate-tasks-to-files.md"
    if skill_path.is_file():
        ok(".claude/commands/migrate-tasks-to-files.md exists")
    else:
        fail(".claude/commands/migrate-tasks-to-files.md exists")
        return

    content = skill_path.read_text()
    for phrase in ["<sow>-tasks.md", "tasks/<id>.md", "tasks/done", "manual", "never automatic"]:
        if phrase in content:
            ok(f"migrate-tasks-to-files.md mentions '{phrase}'")
        else:
            fail(f"migrate-tasks-to-files.md mentions '{phrase}'")


def _migrate_table_row_to_frontmatter(header_cells, row_cells):
    """Mirrors the column-name mapping described in migrate-tasks-to-files.md step 3."""
    header_map = {h.strip().lower(): i for i, h in enumerate(header_cells)}
    expected = ["id", "task", "owner", "priority", "due", "session", "status", "notes"]
    result = {}
    for i, field in enumerate(expected):
        idx = header_map.get(field, i if i < len(row_cells) else None)
        result[field] = row_cells[idx].strip() if idx is not None and idx < len(row_cells) else ""
    # unescape literal pipes that were escaped for table syntax
    result["notes"] = result["notes"].replace("\\|", "|")
    return result


def test_migrate_tasks_parsing():
    section("Migration table -> frontmatter parsing")

    header = ["ID", "Task", "Owner", "Priority", "Due", "Session", "Status", "Notes"]

    row = ["kickoff-01", "Send agenda", "bruno", "high", "", "kickoff", "open", ""]
    parsed = _migrate_table_row_to_frontmatter(header, row)
    if parsed["id"] == "kickoff-01" and parsed["due"] == "":
        ok("Row with empty Due parses with empty due field")
    else:
        fail("Row with empty Due parses with empty due field", repr(parsed))

    row2 = ["t-01", "Fix bug", "bruno", "high", "", "tech", "open", "blocked\\|waiting on client"]
    parsed2 = _migrate_table_row_to_frontmatter(header, row2)
    if parsed2["notes"] == "blocked|waiting on client":
        ok("Escaped pipe in Notes is unescaped back to a literal '|'")
    else:
        fail("Escaped pipe in Notes is unescaped", repr(parsed2))


def test_sow_config_template():
    section("sows/_template/sow.config.yaml")
    repo = Path(__file__).parent.parent
    content = (repo / "sows/_template/sow.config.yaml").read_text()

    for field in [
        "ENGAGEMENT_TYPE", "ENGAGEMENT_CONTEXT",
        "DRIVE_FOLDERS", "MEETING_FILTER", "SOW_DOC_URL",
        "SLACK_CHANNELS", "GEMINI_NOTES_DOCS", "sow_lead",
    ]:
        if field in content:
            ok(f"{field} present in template")
        else:
            fail(f"{field} present in template")


# ─── sow.config.yaml parsing ─────────────────────────────────────────────────

def test_sow_config_parsing():
    section("sow.config.yaml parsing")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        config_content = '''ENGAGEMENT_TYPE: "POC"
ENGAGEMENT_CONTEXT: "Loka is building a RAG system."
DRIVE_FOLDERS: "https://drive.google.com/drive/folders/abc123"
MEETING_FILTER: "ZenQMS"
SOW_DOC_URL: ""
SLACK_CHANNELS: "#client-sow3-general, #client-sow3-dev"
GEMINI_NOTES_DOCS: ""
sow_lead: "ronny"
'''
        (tmp / "sow.config.yaml").write_text(config_content)

        parsed = {}
        for line in config_content.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            key, _, value = line.partition(":")
            parsed[key.strip()] = value.strip().strip('"').strip("'")

        if parsed.get("sow_lead") == "ronny":
            ok("sow_lead parsed correctly")
        else:
            fail("sow_lead parsed", repr(parsed.get("sow_lead")))

        if parsed.get("ENGAGEMENT_TYPE") == "POC":
            ok("ENGAGEMENT_TYPE parsed correctly")
        else:
            fail("ENGAGEMENT_TYPE parsed", repr(parsed.get("ENGAGEMENT_TYPE")))

        channels = [c.strip() for c in parsed.get("SLACK_CHANNELS", "").split(",")]
        if len(channels) == 2 and channels[0] == "#client-sow3-general":
            ok("SLACK_CHANNELS split into 2 channels")
        else:
            fail("SLACK_CHANNELS split", repr(channels))

        if parsed.get("SOW_DOC_URL") == "":
            ok("Empty fields parse as empty string")
        else:
            fail("Empty fields parse as empty string", repr(parsed.get("SOW_DOC_URL")))


# ─── /sync-tasks ──────────────────────────────────────────────────────────────

def test_sync_tasks_config_and_skill():
    section("sync-tasks config + skill")
    repo = Path(__file__).parent.parent

    config_content = (repo / "sows/_template/sow.config.yaml").read_text()
    for field in ["TASK_BOARD_SHEET_ID", "TASK_BOARD_SHEET_URL", "TASK_BOARD_FOLDER_ID"]:
        if field in config_content:
            ok(f"{field} present in sow.config.yaml template")
        else:
            fail(f"{field} present in sow.config.yaml template")

    skill_path = repo / ".claude/commands/sync-tasks.md"
    if skill_path.is_file():
        ok(".claude/commands/sync-tasks.md exists")
    else:
        fail(".claude/commands/sync-tasks.md exists")
        return

    skill_content = skill_path.read_text()
    for phrase in ["create_file", "TASK_BOARD_SHEET_ID", "TASK_BOARD_SHEET_URL", "new spreadsheet", "TASK_BOARD_FOLDER_ID", "tasks/*.md"]:
        if phrase in skill_content:
            ok(f"sync-tasks.md mentions '{phrase}'")
        else:
            fail(f"sync-tasks.md mentions '{phrase}'")

    if "Parse `DRIVE_FOLDERS`" not in skill_content:
        ok("sync-tasks.md no longer derives parentId from DRIVE_FOLDERS")
    else:
        fail("sync-tasks.md no longer derives parentId from DRIVE_FOLDERS")

    if "<sow>-tasks.md" not in skill_content:
        ok("sync-tasks.md no longer reads a shared table file")
    else:
        fail("sync-tasks.md no longer reads a shared table file")


# ─── /sync-tasks folder backfill (upgrade.sh) ─────────────────────────────────

def test_upgrade_backfills_task_board_folder_id():
    section("template-upgrade-repos backfills TASK_BOARD_FOLDER_ID")
    repo = Path(__file__).parent.parent

    upgrade_content = (repo / ".claude/commands/template-upgrade-repos.md").read_text()
    if "TASK_BOARD_FOLDER_ID" in upgrade_content:
        ok("template-upgrade-repos.md documents TASK_BOARD_FOLDER_ID backfill logic")
    else:
        fail("template-upgrade-repos.md documents TASK_BOARD_FOLDER_ID backfill logic")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir)

        # SOW missing the field entirely — should get it appended
        missing = target / "sows/sow1"
        missing.mkdir(parents=True)
        (missing / "sow.config.yaml").write_text('DRIVE_FOLDERS: "https://drive.google.com/drive/folders/abc"\n')

        # SOW that already has the field — should be left untouched
        present = target / "sows/sow2"
        present.mkdir(parents=True)
        (present / "sow.config.yaml").write_text(
            'DRIVE_FOLDERS: ""\nTASK_BOARD_FOLDER_ID: "already-set"\n'
        )

        # _template — backfill loop must skip it (handled by the plain file copy instead)
        template = target / "sows/_template"
        template.mkdir(parents=True)
        (template / "sow.config.yaml").write_text('DRIVE_FOLDERS: ""\n')

        backfill_script = f"""
        set -e
        TARGET="{target}"
        for config in "$TARGET"/sows/*/sow.config.yaml; do
            [ -f "$config" ] || continue
            case "$config" in
                "$TARGET/sows/_template/sow.config.yaml") continue ;;
            esac
            if ! grep -q "^TASK_BOARD_FOLDER_ID:" "$config"; then
                echo 'TASK_BOARD_FOLDER_ID: ""' >> "$config"
            fi
        done
        """
        result = subprocess.run(["bash", "-c", backfill_script], capture_output=True)
        if result.returncode != 0:
            fail("backfill script ran", result.stderr.decode())
            return

        missing_content = (missing / "sow.config.yaml").read_text()
        if 'TASK_BOARD_FOLDER_ID: ""' in missing_content:
            ok("field appended to SOW config missing it")
        else:
            fail("field appended to SOW config missing it", repr(missing_content))

        present_content = (present / "sow.config.yaml").read_text()
        if present_content.count("TASK_BOARD_FOLDER_ID") == 1 and "already-set" in present_content:
            ok("existing field left untouched, not duplicated")
        else:
            fail("existing field left untouched, not duplicated", repr(present_content))

        template_content = (template / "sow.config.yaml").read_text()
        if "TASK_BOARD_FOLDER_ID" not in template_content:
            ok("_template skipped by backfill loop")
        else:
            fail("_template skipped by backfill loop", repr(template_content))


def _parse_frontmatter(text):
    """Minimal YAML-frontmatter parser, mirrors what sync-tasks.md expects Claude to do."""
    lines = text.strip().splitlines()
    assert lines[0].strip() == "---"
    fm = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fm[key.strip()] = value.strip().strip('"').strip("'")
    return fm


def _notes_body(text):
    if "## Notes" not in text:
        return ""
    body = text.split("## Notes", 1)[1]
    return " ".join(line.strip() for line in body.strip().splitlines() if line.strip())


def _csv_escape(cell):
    if any(ch in cell for ch in [",", '"', "\n"]):
        return '"' + cell.replace('"', '""') + '"'
    return cell


def _task_files_to_csv(files):
    """Mirrors the parsing algorithm described in .claude/commands/sync-tasks.md."""
    header = ["ID", "Task", "Owner", "Priority", "Due", "Session", "Status", "Notes"]
    fields = ["id", "task", "owner", "priority", "due", "session", "status"]
    rows = []
    for f in sorted(files, key=lambda t: _parse_frontmatter(t)["id"]):
        fm = _parse_frontmatter(f)
        row = [fm.get(field, "") for field in fields] + [_notes_body(f)]
        rows.append(row)
    lines = [",".join(header)]
    lines += [",".join(_csv_escape(c) for c in row) for row in rows]
    return "\n".join(lines)


def test_task_board_csv_parsing():
    section("Task files -> CSV parsing")

    csv = _task_files_to_csv([])
    if csv == "ID,Task,Owner,Priority,Due,Session,Status,Notes":
        ok("No task files produces header-only CSV")
    else:
        fail("No task files produces header-only CSV", repr(csv))

    normal = """---
id: kickoff-01
task: "Send agenda"
owner: bruno
priority: high
due: 2026-07-10
session: kickoff
status: open
---
"""
    csv = _task_files_to_csv([normal])
    lines = csv.splitlines()
    if len(lines) == 2 and lines[1].split(",")[:3] == ["kickoff-01", "Send agenda", "bruno"]:
        ok("Normal task file parses into the right fields")
    else:
        fail("Normal task file parses into the right fields", repr(lines))

    comma_notes = """---
id: t-01
task: "Fix bug"
owner: bruno
priority: high
due:
session: tech
status: open
---

## Notes

blocked, waiting on client
"""
    csv = _task_files_to_csv([comma_notes])
    if '"blocked, waiting on client"' in csv:
        ok("Notes containing a comma is quoted")
    else:
        fail("Notes containing a comma is quoted", repr(csv))

    quote_notes = """---
id: t-02
task: 'Say hi'
owner: bruno
priority: low
due:
session: tech
status: open
---

## Notes

Client said "hi" in the call
"""
    csv = _task_files_to_csv([quote_notes])
    if '"Client said ""hi"" in the call"' in csv:
        ok("Notes containing a double quote is escaped and wrapped")
    else:
        fail("Notes containing a double quote is escaped and wrapped", repr(csv))

    multi = [normal, comma_notes]
    csv = _task_files_to_csv(multi)
    ids = [line.split(",")[0] for line in csv.splitlines()[1:]]
    if ids == ["kickoff-01", "t-01"]:
        ok("Rows sorted by id for a stable export order")
    else:
        fail("Rows sorted by id for a stable export order", repr(ids))


# ─── /upgrade file coverage ───────────────────────────────────────────────────

def test_upgrade_covers_all_commands():
    section("/upgrade command coverage")
    repo = Path(__file__).parent.parent
    upgrade_content = (repo / ".claude/commands/upgrade.md").read_text()

    # Maintainer-only commands never ship to client vaults, so /upgrade
    # intentionally doesn't list them among the files it copies.
    maintainer_only = {"template-commit-n-release.md", "template-upgrade-repos.md"}

    commands_dir = repo / ".claude/commands"
    for cmd_file in sorted(commands_dir.glob("*.md")):
        if cmd_file.name in maintainer_only:
            continue
        rel = f".claude/commands/{cmd_file.name}"
        if rel in upgrade_content:
            ok(f"{rel} listed in /upgrade's file list")
        else:
            fail(f"{rel} listed in /upgrade's file list")


# ─── Bundled skills ───────────────────────────────────────────────────────────

def test_bundled_skills():
    section("Bundled skills")
    repo = Path(__file__).parent.parent

    for skill in ["github-commit", "github-branch-publish", "github-branch-refresh"]:
        skill_path = repo / f".claude/skills/{skill}/SKILL.md"
        if skill_path.is_file():
            ok(f".claude/skills/{skill}/SKILL.md exists")
        else:
            fail(f".claude/skills/{skill}/SKILL.md exists")

    bootstrap_content = (repo / ".claude/commands/bootstrap.md").read_text()
    for skill in ["github-commit", "github-branch-publish"]:
        clone_line = f"cp -r /tmp/claude-skills-bootstrap/{skill} .claude/skills/{skill}"
        if clone_line not in bootstrap_content:
            ok(f"bootstrap.md no longer clones {skill} from claude-skills")
        else:
            fail(f"bootstrap.md no longer clones {skill} from claude-skills")

    if "cp -r /tmp/claude-skills-bootstrap/action-board" in bootstrap_content:
        ok("bootstrap.md still clones action-board from claude-skills")
    else:
        fail("bootstrap.md still clones action-board from claude-skills")

    upgrade_content = (repo / ".claude/commands/upgrade.md").read_text()
    if ".claude/skills/" in upgrade_content:
        ok(".claude/skills/ listed in /upgrade's file list")
    else:
        fail(".claude/skills/ listed in /upgrade's file list")


# ─── SOW branch naming ────────────────────────────────────────────────────────

def test_sow_branch_naming():
    section("SOW branch naming")

    def branch_from_sow_dir(sow_dir_name):
        return sow_dir_name  # convention: sow3 dir → sow3 branch

    cases = [
        ("sow1", "sow1"),
        ("sow3", "sow3"),
        ("sow10", "sow10"),
    ]
    for sow_dir, expected_branch in cases:
        got = branch_from_sow_dir(sow_dir)
        if got == expected_branch:
            ok(f"'{sow_dir}' dir → branch '{expected_branch}'")
        else:
            fail(f"'{sow_dir}' dir → branch '{expected_branch}'", f"got '{got}'")


# ─── Placeholder replacement ──────────────────────────────────────────────────

def test_placeholder_replacement():
    section("Placeholder replacement (synthetic vault)")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        (tmp / "CLAUDE.md").write_text(
            "# {{CLIENT_NAME}} Engagement\nOwner: {{OWNER_NAME}} ({{OWNER_ROLE}})\n"
        )
        (tmp / "notes").mkdir()
        (tmp / "notes" / "note.md").write_text("No placeholders here.\n")

        config = {
            "CLIENT_NAME": "ACME Corp",
            "OWNER_NAME": "Bruno Costa",
            "OWNER_ROLE": "TPM",
        }

        for key, value in config.items():
            placeholder = f"{{{{{key}}}}}"
            result = subprocess.run(
                ["bash", "-c",
                 f"find {tmp} -name '*.md' -print0 | xargs -0 sed -i 's|{placeholder}|{value}|g'"],
                capture_output=True
            )
            if result.returncode != 0:
                fail(f"sed replacement for {key}", result.stderr.decode())

        content = (tmp / "CLAUDE.md").read_text()

        if "ACME Corp" in content and "{{CLIENT_NAME}}" not in content:
            ok("CLIENT_NAME replaced")
        else:
            fail("CLIENT_NAME replaced", repr(content))

        if "Bruno Costa" in content and "TPM" in content:
            ok("OWNER_NAME and OWNER_ROLE replaced")
        else:
            fail("OWNER_NAME and OWNER_ROLE replaced")

        if (tmp / "notes" / "note.md").read_text() == "No placeholders here.\n":
            ok("Files without placeholders untouched")
        else:
            fail("Files without placeholders untouched")

        result = subprocess.run(
            ["grep", "-r", "{{", str(tmp), "--include=*.md"],
            capture_output=True
        )
        if result.returncode != 0:
            ok("No placeholders remain after replacement")
        else:
            fail("No placeholders remain", result.stdout.decode().strip())


# ─── Bootstrap state file ─────────────────────────────────────────────────────

def test_bootstrap_state():
    section("Bootstrap state file")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        state_path = tmp / ".bootstrap-state.md"

        state_path.write_text("""last_ran: 2026-06-05
sows_processed: sow3, sow4
""")

        content = state_path.read_text()

        last_ran = None
        for line in content.splitlines():
            if line.startswith("last_ran:"):
                last_ran = line.split(":", 1)[1].strip()
                break

        if last_ran == "2026-06-05":
            ok("last_ran readable from state file")
        else:
            fail("last_ran readable", repr(last_ran))

        if "sow3" in content and "sow4" in content:
            ok("sows_processed written correctly")
        else:
            fail("sows_processed written correctly")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("ai-project-2ndbrain Test Suite")
    print("=" * 40)

    test_repo_structure()
    test_gitignore()
    test_config_example()
    test_sow_task_board()
    test_migrate_tasks_command()
    test_migrate_tasks_parsing()
    test_sow_config_template()
    test_sow_config_parsing()
    test_sync_tasks_config_and_skill()
    test_upgrade_backfills_task_board_folder_id()
    test_task_board_csv_parsing()
    test_upgrade_covers_all_commands()
    test_bundled_skills()
    test_sow_branch_naming()
    test_placeholder_replacement()
    test_bootstrap_state()

    print()
    print("=" * 40)
    total = passed + failed
    print(f"Results: {passed}/{total} passed", end="")
    if failed:
        print(f", {failed} FAILED", end="")
    print()

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
