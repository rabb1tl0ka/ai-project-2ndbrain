#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="$SCRIPT_DIR/project.config.yaml"
CONFIG_EXAMPLE="$SCRIPT_DIR/project.config.example.yaml"
VAULT="$SCRIPT_DIR/project-vault"

echo ""
echo "Project Brain Setup"
echo "==================="
echo ""

# ── Checks ────────────────────────────────────────────────────────────────────

warnings=0

# Claude Code
if ! command -v claude &>/dev/null; then
  echo "  ⚠  Claude Code is not installed."
  echo "     It's required to use your project brain."
  echo ""
  read -rp "     Install it now? [y/N]: " install_claude
  if [[ "$install_claude" =~ ^[Yy]$ ]]; then
    echo ""
    echo "     Running: curl -fsSL https://claude.ai/install.sh | bash"
    echo ""
    curl -fsSL https://claude.ai/install.sh | bash
    echo ""
    if command -v claude &>/dev/null; then
      echo "  ✓  Claude Code installed."
    else
      echo "  ⚠  Installation may have failed. Check the output above."
      echo "     You can install manually: https://claude.ai/code"
    fi
  else
    echo "     Skipping. Install manually when ready: https://claude.ai/code"
  fi
  echo ""
  ((warnings++)) || true
fi

# Auto-copy example config if project.config.yaml doesn't exist
if [[ ! -f "$CONFIG" ]]; then
  cp "$CONFIG_EXAMPLE" "$CONFIG"
  echo "  ✓  Created project.config.yaml from project.config.example.yaml"
  echo ""
  echo "  Fill in your details in project.config.yaml, then re-run ./setup.sh"
  echo ""
  exit 0
fi

# Detect unfilled config defaults
defaults=("Your Client" "Your Name" "Your Role" "@yourhandle" "Your Engagement Type")
for default in "${defaults[@]}"; do
  if grep -qF "\"$default\"" "$CONFIG" 2>/dev/null; then
    echo "  ⚠  project.config.yaml still has default values (e.g. \"$default\")."
    echo "     Fill in your details before running setup."
    echo ""
    ((warnings++)) || true
    break
  fi
done

if [[ $warnings -eq 0 ]]; then
  echo "  ✓  All checks passed."
  echo ""
fi

# ── Apply config ───────────────────────────────────────────────────────────────

echo "Applying config..."
echo ""

first_sow=""

while IFS= read -r line; do
  [[ "$line" =~ ^[[:space:]]*# ]] && continue
  [[ -z "${line// }" ]] && continue
  [[ "$line" != *:* ]] && continue

  key="${line%%:*}"
  value="${line#*: }"
  key="${key// /}"
  value="${value# }"
  value="${value#\"}"
  value="${value%\"}"
  value="${value#\'}"
  value="${value%\'}"

  [[ -z "$key" || -z "$value" ]] && continue

  # Capture FIRST_SOW for directory creation step
  if [[ "$key" == "FIRST_SOW" ]]; then
    first_sow="$value"
  fi

  placeholder="{{${key}}}"
  count=0

  while IFS= read -r -d '' file; do
    if grep -qF "$placeholder" "$file" 2>/dev/null; then
      sed -i "s|${placeholder}|${value}|g" "$file"
      ((count++)) || true
    fi
  done < <(find "$VAULT" -name "*.md" -print0)

  printf "  %-25s → %s  (%d file(s))\n" "{{${key}}}" "$value" "$count"
done < "$CONFIG"

echo ""

# ── Create first SOW from template ────────────────────────────────────────────

if [[ -n "$first_sow" ]]; then
  SOW_DIR="$VAULT/sows/$first_sow"
  TEMPLATE_DIR="$VAULT/sows/_template"

  if [[ ! -d "$SOW_DIR" ]]; then
    cp -r "$TEMPLATE_DIR" "$SOW_DIR"
    # Rename the sow-reference file to match the SOW name
    if [[ -f "$SOW_DIR/sow-reference.md" ]]; then
      mv "$SOW_DIR/sow-reference.md" "$SOW_DIR/${first_sow}-reference.md"
    fi
    echo "  ✓  Created sows/$first_sow/ from template"
    echo ""
  else
    echo "  ✓  sows/$first_sow/ already exists — skipped"
    echo ""
  fi
fi

# ── Verify ─────────────────────────────────────────────────────────────────────

missed=()
while IFS= read -r line; do
  [[ "$line" =~ ^[[:space:]]*# ]] && continue
  [[ -z "${line// }" ]] && continue
  [[ "$line" != *:* ]] && continue
  key="${line%%:*}"
  key="${key// /}"
  [[ -z "$key" ]] && continue
  if grep -rqF "{{${key}}}" "$VAULT" --include="*.md" 2>/dev/null; then
    missed+=("{{${key}}}")
  fi
done < "$CONFIG"

if [[ ${#missed[@]} -gt 0 ]]; then
  echo "⚠  These tags were not replaced (check project.config.yaml for empty values):"
  for tag in "${missed[@]}"; do
    echo "   $tag"
  done
  echo ""
else
  echo "✓  All config tags replaced."
  echo ""
fi

# ── Next steps ─────────────────────────────────────────────────────────────────

echo "Next steps:"
echo ""
echo "  1. Create a new GitHub repo for this project brain (e.g. LokaHQ/my-client-ai-2ndbrain)"
echo "     and push this configured repo there:"
echo ""
echo "       git remote set-url origin <your-new-repo-url>"
echo "       git add -A && git commit -m \"init: configure project brain\""
echo "       git push -u origin main"
echo ""
echo "  2. Open project-vault/ in Obsidian (or any markdown editor)."
echo ""
if command -v claude &>/dev/null; then
  echo "  3. Spawn Claude Code inside the vault:"
  echo "       cd \"$VAULT\" && claude"
else
  echo "  3. Install Claude Code (https://claude.ai/code), then:"
  echo "       cd \"$VAULT\" && claude"
fi
echo ""
echo "  4. Fill in project-vault/CLAUDE.md with your team and stakeholder details."
echo ""
echo "  5. Start."
echo ""
