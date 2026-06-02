#!/bin/bash
# Upgrade an existing ai-project-2ndbrain install to the current version.
#
# Copies pure tooling files (commands, templates, conventions).
# Never touches project-specific content (CLAUDE.md in vault, sow dirs, stakeholders, notes).
#
# Usage: bash upgrade.sh <target-repo-path> [--create-pr]
# Example: bash upgrade.sh ~/loka/projects/health-edge-ai-2ndbrain
#          bash upgrade.sh ~/loka/projects/health-edge-ai-2ndbrain --create-pr

set -e

TARGET="$1"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ── Flag parsing ──────────────────────────────────────────────────────────────

CREATE_PR=false
for arg in "$@"; do
    case $arg in
        --create-pr) CREATE_PR=true ;;
    esac
done

# ── Validation ────────────────────────────────────────────────────────────────

if [ -z "$TARGET" ]; then
    echo "Usage: bash upgrade.sh <target-repo-path> [--create-pr]"
    exit 1
fi

if [ ! -d "$TARGET" ]; then
    echo "Error: target directory '$TARGET' does not exist."
    exit 1
fi

if [ ! -d "$TARGET/.git" ]; then
    echo "Error: '$TARGET' is not a git repository."
    exit 1
fi

if [ ! -f "$TARGET/project-vault/CLAUDE.md" ]; then
    echo "Error: '$TARGET' doesn't look like an ai-project-2ndbrain repo (project-vault/CLAUDE.md missing)."
    exit 1
fi

if ! git -C "$TARGET" diff --quiet 2>/dev/null || ! git -C "$TARGET" diff --cached --quiet 2>/dev/null; then
    echo "Warning: '$TARGET' has uncommitted changes. Continuing anyway."
fi

# ── Version info ──────────────────────────────────────────────────────────────

CURRENT_TAG=$(git -C "$SCRIPT_DIR" describe --tags --abbrev=0 2>/dev/null || echo "untagged")
VERSION_FILE="$TARGET/.2ndbrain-version"

if [ -f "$VERSION_FILE" ]; then
    LAST_TAG=$(cat "$VERSION_FILE")
else
    LAST_TAG="v0 (no .2ndbrain-version found)"
fi

echo "=== ai-project-2ndbrain upgrade ==="
echo "Version: $LAST_TAG → $CURRENT_TAG"
echo "Target:  $TARGET"
echo ""

# ── Files to upgrade ─────────────────────────────────────────────────────────
# Pure tooling only. project-vault/CLAUDE.md is intentionally excluded —
# it gets personalized by /onboard and must not be overwritten.

copy_file() {
    local rel="$1"
    local src="$SCRIPT_DIR/$rel"
    local dst="$TARGET/$rel"

    if [ ! -f "$src" ]; then
        return  # file doesn't exist in template (e.g. new addition not yet released)
    fi

    mkdir -p "$(dirname "$dst")"
    cp "$src" "$dst"
    echo "✅ $rel"
}

copy_dir() {
    local rel="$1"
    local src="$SCRIPT_DIR/$rel"
    local dst="$TARGET/$rel"

    if [ ! -d "$src" ]; then
        return
    fi

    mkdir -p "$dst"
    cp -r "$src/." "$dst/"
    echo "✅ $rel/"
}

echo "Copying tooling files..."
echo ""

# Root-level commands and config
copy_file ".claude/commands/2ndbrain.md"
copy_file ".claude/commands/onboard.md"
copy_file "CLAUDE.md"
copy_file "README.md"
copy_file "project.config.example.yaml"

# Vault commands (the core of what users run)
copy_file "project-vault/.claude/commands/bootstrap.md"
copy_file "project-vault/.claude/commands/meeting-recap.md"
copy_file "project-vault/.claude/commands/publish-to-notion.md"

# SOW template (safe — not an actual SOW, just the blank starting point)
copy_file "project-vault/sows/_template/sow.config.yaml"
copy_file "project-vault/sows/_template/sow-reference.md"

# Vault templates (meeting summary, TLU, working session)
copy_dir "project-vault/templates"

# Roadmap conventions and item templates (engagement roadmap)
copy_file "project-vault/roadmap/CLAUDE.md"
copy_dir "project-vault/roadmap/templates"

# .kernel conventions (brain repo internal roadmap)
copy_file ".kernel/roadmap/CLAUDE.md"

echo ""

# ── Ensure new directories exist ─────────────────────────────────────────────

# publish-to-notion is new — target may not have the command dir setting yet
if [ ! -f "$TARGET/project-vault/.claude/settings.local.json" ] && [ -f "$SCRIPT_DIR/project-vault/.claude/settings.local.json" ]; then
    copy_file "project-vault/.claude/settings.local.json"
fi

# ── Update version file ───────────────────────────────────────────────────────

echo "$CURRENT_TAG" > "$VERSION_FILE"
echo "✅ .2ndbrain-version → $CURRENT_TAG"
echo ""

# ── Commit and optionally create PR ──────────────────────────────────────────

if [ "$CREATE_PR" = true ]; then
    BRANCH="chore/2ndbrain-upgrade-${CURRENT_TAG}"

    if git -C "$TARGET" show-ref --verify --quiet "refs/heads/$BRANCH"; then
        echo "⚠️  Branch '$BRANCH' already exists. Delete it or merge before re-running."
        exit 1
    fi

    git -C "$TARGET" checkout -b "$BRANCH"
    git -C "$TARGET" add \
        .claude/commands/ \
        CLAUDE.md README.md project.config.example.yaml \
        project-vault/.claude/commands/ \
        project-vault/sows/_template/ \
        project-vault/templates/ \
        project-vault/roadmap/CLAUDE.md \
        project-vault/roadmap/templates/ \
        .kernel/roadmap/CLAUDE.md \
        .2ndbrain-version 2>/dev/null || true
    git -C "$TARGET" commit -m "chore: upgrade ai-project-2ndbrain ${LAST_TAG} → ${CURRENT_TAG}"
    git -C "$TARGET" push -u origin "$BRANCH"
    echo "✅ Branch '$BRANCH' pushed"

    if ! command -v gh &>/dev/null; then
        echo ""
        echo "⚠️  GitHub CLI (gh) not found — create the PR manually."
        exit 0
    fi

    if ! gh auth status &>/dev/null; then
        echo ""
        echo "⚠️  gh not authenticated — create the PR manually or run: gh auth login"
        exit 0
    fi

    CHANGELOG=$(git -C "$SCRIPT_DIR" log "${LAST_TAG}..HEAD" --oneline 2>/dev/null || true)
    if [ -z "$CHANGELOG" ]; then
        CHANGELOG_MD="- No changelog available (tags missing or first install)."
    else
        CHANGELOG_MD=$(echo "$CHANGELOG" | sed 's/^/- /')
    fi

    DEFAULT_BRANCH=$(cd "$TARGET" && gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main")

    PR_URL=$(cd "$TARGET" && gh pr create \
        --base "$DEFAULT_BRANCH" \
        --head "$BRANCH" \
        --title "chore: upgrade ai-project-2ndbrain ${LAST_TAG} → ${CURRENT_TAG}" \
        --body "$(cat <<EOF
## ai-project-2ndbrain upgrade: ${LAST_TAG} → ${CURRENT_TAG}

Tooling-only upgrade. Project content (vault CLAUDE.md, SOW dirs, stakeholders, notes) is untouched.

### What changed upstream
${CHANGELOG_MD}

### What was updated
- \`.claude/commands/\` — root commands
- \`project-vault/.claude/commands/\` — vault commands (bootstrap, meeting-recap, publish-to-notion)
- \`project-vault/sows/_template/\` — SOW config template
- \`project-vault/templates/\` — meeting summary, TLU, working session templates
- \`project-vault/roadmap/\` — roadmap conventions and templates
EOF
)")

    echo ""
    echo "✅ PR created: $PR_URL"
else
    echo "Upgrade complete. Review changes then commit:"
    echo ""
    echo "  cd $TARGET"
    echo "  git add .claude/ CLAUDE.md README.md project.config.example.yaml \\"
    echo "          project-vault/.claude/ project-vault/sows/_template/ \\"
    echo "          project-vault/templates/ project-vault/roadmap/CLAUDE.md \\"
    echo "          project-vault/roadmap/templates/ .kernel/roadmap/CLAUDE.md \\"
    echo "          .2ndbrain-version"
    echo "  git commit -m 'chore: upgrade ai-project-2ndbrain ${LAST_TAG} → ${CURRENT_TAG}'"
    echo ""
    echo "  To create a PR instead: bash upgrade.sh $TARGET --create-pr"
fi
