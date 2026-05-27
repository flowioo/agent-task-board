#!/usr/bin/env bash
# Install agent-task-board skills for Hermes Agent
# Usage: bash install.sh [--force]
#
# Creates symlinks from ~/.hermes/skills/ to the skills/ directory in this repo.
# Safe to run multiple times — skips existing links unless --force is passed.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HERMES_SKILLS="${HERMES_HOME:-$HOME/.hermes}/skills"
FORCE=false

[[ "${1:-}" == "--force" ]] && FORCE=true

mkdir -p "$HERMES_SKILLS"

for skill_dir in "$SCRIPT_DIR/skills"/*/; do
    skill_name="$(basename "$skill_dir")"
    target="$HERMES_SKILLS/$skill_name"

    if [[ -L "$target" ]]; then
        if $FORCE; then
            rm "$target"
            echo "replaced: $target"
        else
            echo "skip (exists): $target"
            continue
        fi
    elif [[ -d "$target" ]]; then
        echo "conflict (real dir): $target — use --force to replace"
        continue
    fi

    ln -s "$skill_dir" "$target"
    echo "installed: $skill_name → $target"
done

# Ensure ~/.project exists
mkdir -p "$HOME/.project/reports"

echo ""
echo "Done. Open board: open ~/.project/board.html"
