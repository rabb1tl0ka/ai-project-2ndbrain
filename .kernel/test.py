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
        "sows/_template/done",
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
        "sows/_template/sow-tasks.md",
        "sows/_template/CLAUDE.md",
        ".claude/commands/onboard.md",
        ".claude/commands/bootstrap.md",
        ".claude/commands/2ndbrain.md",
        ".claude/commands/meeting-recap.md",
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

    if (repo / "sows/_template/sow-tasks.md").is_file():
        ok("sows/_template/sow-tasks.md exists")
    else:
        fail("sows/_template/sow-tasks.md exists")

    if (repo / "sows/_template/done/.gitkeep").is_file():
        ok("sows/_template/done/.gitkeep exists")
    else:
        fail("sows/_template/done/.gitkeep exists")

    tasks_content = (repo / "sows/_template/sow-tasks.md").read_text()
    for col in ["ID", "Task", "Owner", "Priority", "Due", "Session", "Status", "Notes"]:
        if col in tasks_content:
            ok(f"sow-tasks.md has '{col}' column")
        else:
            fail(f"sow-tasks.md has '{col}' column")

    claude_content = (repo / "sows/_template/CLAUDE.md").read_text()
    if "{{SOW_NAME}}" in claude_content:
        ok("sows/_template/CLAUDE.md has {{SOW_NAME}} placeholder")
    else:
        fail("sows/_template/CLAUDE.md has {{SOW_NAME}} placeholder")

    if "priority" in claude_content.lower():
        ok("sows/_template/CLAUDE.md references priority inference")
    else:
        fail("sows/_template/CLAUDE.md references priority inference")

    onboard = (repo / ".claude/commands/onboard.md").read_text()
    if "sow-tasks.md" in onboard and "<sow>-tasks.md" in onboard:
        ok("/onboard renames sow-tasks.md → <sow>-tasks.md")
    else:
        fail("/onboard renames sow-tasks.md → <sow>-tasks.md")

    if "{{SOW_NAME}}" in onboard and "sed" in onboard:
        ok("/onboard replaces {{SOW_NAME}} placeholder")
    else:
        fail("/onboard replaces {{SOW_NAME}} placeholder")

    root_claude = (repo / "CLAUDE.md").read_text()
    if "sows/<sow>/CLAUDE.md" in root_claude:
        ok("root CLAUDE.md references per-SOW CLAUDE.md")
    else:
        fail("root CLAUDE.md references per-SOW CLAUDE.md")


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
    test_sow_config_template()
    test_sow_config_parsing()
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
