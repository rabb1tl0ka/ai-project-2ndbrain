#!/bin/bash
# Upgrade an existing ai-project-2ndbrain install to the current version.
#
# Copies pure tooling files (commands, templates, conventions).
# Never touches project-specific content (CLAUDE.md after onboard, sow dirs,
# stakeholders, team, notes, inbox, archive).
#
# Run this FROM the template repo, pointing AT the target repo:
#   bash .kernel/upgrade.sh ~/loka/projects/zenqms-ai-2ndbrain
#   bash .kernel/upgrade.sh ~/loka/projects/zenqms-ai-2ndbrain --create-pr

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"   # template repo root
TARGET="$1"

# ── Flag parsing ──────────────────────────────────────────────────────────────

CREATE_PR=false
for arg in "$@"; do
    case $arg in
        --create-pr) CREATE_PR=true ;;
    esac
done

# ── Validation ────────────────────────────────────────────────────────────────

if [ -z "$TARGET" ]; then
    echo "Usage: bash .kernel/upgrade.sh <target-repo-path> [--create-pr]"
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

if [ ! -f "$TARGET/CLAUDE.md" ] || [ ! -d "$TARGET/sows" ]; then
    echo "Error: '$TARGET' doesn't look like an ai-project-2ndbrain repo (CLAUDE.md or sows/ missing)."
    exit 1
fi

if ! git -C "$TARGET" diff --quiet 2>/dev/null || ! git -C "$TARGET" diff --cached --quiet 2>/dev/null; then
    echo "Warning: '$TARGET' has uncommitted changes. Continuing anyway."
fi

# ── Version info ──────────────────────────────────────────────────────────────

CURRENT_TAG=$(git -C "$REPO_DIR" describe --tags --abbrev=0 2>/dev/null || echo "untagged")
VERSION_FILE="$TARGET/.kernel/.2ndbrain-version"

if [ -f "$VERSION_FILE" ]; then
    LAST_TAG=$(cat "$VERSION_FILE")
else
    LAST_TAG="v0 (no .2ndbrain-version found)"
fi

echo "=== ai-project-2ndbrain upgrade ==="
echo "Version: $LAST_TAG → $CURRENT_TAG"
echo "Target:  $TARGET"
echo ""

# ── Copy helpers ──────────────────────────────────────────────────────────────

copy_file() {
    local rel="$1"
    local src="$REPO_DIR/$rel"
    local dst="$TARGET/$rel"

    if [ ! -f "$src" ]; then
        return
    fi

    mkdir -p "$(dirname "$dst")"
    cp "$src" "$dst"
    echo "  ✓ $rel"
}

copy_dir() {
    local rel="$1"
    local src="$REPO_DIR/$rel"
    local dst="$TARGET/$rel"

    if [ ! -d "$src" ]; then
        return
    fi

    mkdir -p "$dst"
    cp -r "$src/." "$dst/"
    echo "  ✓ $rel/"
}

# ── Files to upgrade ─────────────────────────────────────────────────────────
# Tooling only. CLAUDE.md is excluded after onboard — it has real client values.
# sows/, stakeholders/, team/, notes/, inbox/, archive/ are never touched.

echo "Copying tooling files..."
echo ""

# Commands (all in one place now)
copy_file ".claude/commands/2ndbrain.md"
copy_file ".claude/commands/onboard.md"
copy_file ".claude/commands/bootstrap.md"
copy_file ".claude/commands/meeting-recap.md"
copy_file ".claude/commands/publish-to-notion.md"
copy_file ".claude/commands/fetch-from-notion.md"
copy_file ".claude/commands/upgrade.md"

# Config reference (never the actual config.yaml — that's gitignored user data)
copy_file "config.example.yaml"

# README
copy_file "README.md"

# SOW template (safe — not an actual SOW, just the blank starting point)
copy_file "sows/_template/sow.config.yaml"
copy_file "sows/_template/sow-reference.md"

# Vault templates (meeting summary, TLU, working session)
copy_dir "templates"

# Upgrade script itself (so users always have the latest upgrader)
copy_file ".kernel/upgrade.sh"

# Version stamp
mkdir -p "$TARGET/.kernel"
echo "$CURRENT_TAG" > "$VERSION_FILE"
echo "  ✓ .kernel/.2ndbrain-version → $CURRENT_TAG"

echo ""

# ── Commit and optionally create PR ──────────────────────────────────────────

STAGED_PATHS=(
    ".claude/commands/"
    "config.example.yaml"
    "README.md"
    "sows/_template/"
    "templates/"
    ".kernel/.2ndbrain-version"
    ".kernel/upgrade.sh"
)

if [ "$CREATE_PR" = true ]; then
    BRANCH="chore/2ndbrain-upgrade-${CURRENT_TAG}"

    if git -C "$TARGET" show-ref --verify --quiet "refs/heads/$BRANCH"; then
        echo "⚠️  Branch '$BRANCH' already exists. Delete it or merge before re-running."
        exit 1
    fi

    git -C "$TARGET" checkout -b "$BRANCH"
    git -C "$TARGET" add "${STAGED_PATHS[@]}" 2>/dev/null || true
    git -C "$TARGET" commit -m "chore: upgrade ai-project-2ndbrain ${LAST_TAG} → ${CURRENT_TAG}"
    git -C "$TARGET" push -u origin "$BRANCH"
    echo "✓ Branch '$BRANCH' pushed"

    if ! command -v gh &>/dev/null; then
        echo ""
        echo "⚠️  GitHub CLI (gh) not found — create the PR manually."
        exit 0
    fi

    if ! gh auth status &>/dev/null; then
        echo ""
        echo "⚠️  gh not authenticated — run: gh auth login"
        exit 0
    fi

    CHANGELOG=$(git -C "$REPO_DIR" log "${LAST_TAG}..HEAD" --oneline 2>/dev/null || true)
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

Tooling-only upgrade. Project content (CLAUDE.md post-onboard, SOW dirs, stakeholders, team, notes) is untouched.

### What changed upstream
${CHANGELOG_MD}

### What was updated
- \`.claude/commands/\` — all commands (onboard, bootstrap, meeting-recap, publish-to-notion, fetch-from-notion, 2ndbrain)
- \`config.example.yaml\` — config reference
- \`sows/_template/\` — SOW config and reference templates
- \`templates/\` — meeting summary, TLU, working session templates
EOF
)")

    echo ""
    echo "✓ PR created: $PR_URL"
else
    echo "Upgrade complete. Review changes then commit:"
    echo ""
    echo "  cd $TARGET"
    printf "  git add"
    for p in "${STAGED_PATHS[@]}"; do printf " %s" "$p"; done
    echo ""
    echo "  git commit -m 'chore: upgrade ai-project-2ndbrain ${LAST_TAG} → ${CURRENT_TAG}'"
    echo ""
    echo "  To create a PR instead: bash .kernel/upgrade.sh $TARGET --create-pr"
fi
