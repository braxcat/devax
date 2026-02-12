#!/bin/bash
# Publish a sanitized version of devax to the public repo
# Usage: ./scripts/publish.sh [--dry-run]
#
# Reads .devax-publish.json for scrub rules, applies find/replace across all
# tracked files, resets personal history files to clean templates, validates
# that no private terms remain, and pushes to the configured remote.
#
# Exit codes: 0=success, 1=validation failure, 2=config error

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_FILE="$REPO_ROOT/.devax-publish.json"
DRY_RUN=false

# Parse args
for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=true ;;
        --help|-h)
            echo "Usage: $0 [--dry-run]"
            echo "  --dry-run  Show what would change without pushing"
            exit 0
            ;;
        *)
            echo "Error: Unknown argument: $arg"
            echo "Usage: $0 [--dry-run]"
            exit 2
            ;;
    esac
done

# Check config exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file not found: $CONFIG_FILE"
    echo "Create .devax-publish.json with scrub_rules, reset_to_templates, remote, and branch."
    exit 2
fi

# Check dependencies
if ! command -v python3 &>/dev/null; then
    echo "Error: python3 is required (for JSON parsing)"
    exit 2
fi

# Parse config with python3 (available on macOS/Linux, no extra deps)
REMOTE=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['remote'])")
BRANCH=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['branch'])")
NUM_RULES=$(python3 -c "import json; print(len(json.load(open('$CONFIG_FILE'))['scrub_rules']))")
NUM_RESETS=$(python3 -c "import json; print(len(json.load(open('$CONFIG_FILE')).get('reset_to_templates', [])))")
NUM_EXCLUDES=$(python3 -c "import json; print(len(json.load(open('$CONFIG_FILE')).get('exclude_paths', [])))")
NUM_BLOCKLIST=$(python3 -c "import json; print(len(json.load(open('$CONFIG_FILE')).get('validation_blocklist', [])))")

echo "=== Devax Publish ==="
echo "Remote: $REMOTE / $BRANCH"
echo "Scrub rules: $NUM_RULES"
echo "Paths to exclude: $NUM_EXCLUDES"
echo "Files to reset: $NUM_RESETS"
echo "Blocklist terms: $NUM_BLOCKLIST"
if $DRY_RUN; then
    echo "Mode: DRY RUN (no push)"
else
    echo "Mode: LIVE (will push)"
fi
echo ""

# Verify remote exists
REMOTE_URL=$(cd "$REPO_ROOT" && git remote get-url "$REMOTE" 2>/dev/null) || {
    echo "Error: Git remote '$REMOTE' not found in $REPO_ROOT"
    exit 2
}
echo "Remote URL: $REMOTE_URL"
echo ""

# Create temp directory
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

echo "--- Copying tracked files ---"
cd "$REPO_ROOT"

# Copy all git-tracked files to temp dir, preserving directory structure
git ls-files | while IFS= read -r file; do
    dir=$(dirname "$file")
    mkdir -p "$TEMP_DIR/$dir"
    cp "$file" "$TEMP_DIR/$file"
done

FILE_COUNT=$(git ls-files | wc -l | tr -d ' ')
echo "Copied $FILE_COUNT files"
echo ""

# Delete excluded paths
if [ "$NUM_EXCLUDES" -gt 0 ]; then
    echo "--- Removing excluded paths ---"
    for i in $(seq 0 $((NUM_EXCLUDES - 1))); do
        EXCLUDE_PATH=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['exclude_paths'][$i])")
        TARGET="$TEMP_DIR/$EXCLUDE_PATH"
        if [ -e "$TARGET" ]; then
            rm -rf "$TARGET"
            echo "  Removed: $EXCLUDE_PATH"
        else
            echo "  Not found (skipping): $EXCLUDE_PATH"
        fi
    done
    echo ""
fi

# Strip BUSINESS marker sections from all .md files
echo "--- Stripping BUSINESS sections ---"
BUSINESS_COUNT=0
while IFS= read -r mdfile; do
    if grep -q '<!-- BUSINESS:START -->' "$mdfile" 2>/dev/null; then
        sed -i '' '/<!-- BUSINESS:START -->/,/<!-- BUSINESS:END -->/d' "$mdfile"
        REL_PATH="${mdfile#$TEMP_DIR/}"
        echo "  Stripped: $REL_PATH"
        BUSINESS_COUNT=$((BUSINESS_COUNT + 1))
    fi
done < <(find "$TEMP_DIR" -name '*.md' -type f)
echo "  $BUSINESS_COUNT files had BUSINESS sections stripped"
echo ""

# Apply scrub rules via sed on text files only
echo "--- Applying scrub rules ---"
for i in $(seq 0 $((NUM_RULES - 1))); do
    FIND_TERM=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['scrub_rules'][$i]['find'])")
    REPLACE_TERM=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['scrub_rules'][$i]['replace'])")

    # Escape sed special characters in both find and replace
    FIND_ESCAPED=$(printf '%s' "$FIND_TERM" | sed 's/[&/\]/\\&/g; s/\[/\\[/g; s/\]/\\]/g')
    REPLACE_ESCAPED=$(printf '%s' "$REPLACE_TERM" | sed 's/[&/\]/\\&/g')

    # Count matches before replacing (|| true to avoid pipefail exit)
    MATCH_COUNT=$(grep -rl "$FIND_TERM" "$TEMP_DIR" 2>/dev/null | wc -l | tr -d ' ' || true)

    if [ "$MATCH_COUNT" -gt 0 ] 2>/dev/null; then
        echo "  Rule: '$FIND_TERM' -> '$REPLACE_TERM' ($MATCH_COUNT files)"

        # Apply to text files only (skip binary files)
        while IFS= read -r file; do
            if file "$file" | grep -q "text"; then
                sed -i '' "s/${FIND_ESCAPED}/${REPLACE_ESCAPED}/g" "$file"
            fi
        done < <(find "$TEMP_DIR" -type f)
    else
        echo "  Rule: '$FIND_TERM' -> '$REPLACE_TERM' (no matches)"
    fi
done
echo ""

# Reset template files
if [ "$NUM_RESETS" -gt 0 ]; then
    echo "--- Resetting personal history files ---"
    for i in $(seq 0 $((NUM_RESETS - 1))); do
        RESET_FILE=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['reset_to_templates'][$i])")

        if [ -f "$TEMP_DIR/$RESET_FILE" ]; then
            case "$RESET_FILE" in
                *WORKLOG.md)
                    cat > "$TEMP_DIR/$RESET_FILE" << 'TEMPLATE'
# Devax — Work Log

> Development session log. Updated after each work session.

---

<!-- ## Session: YYYY-MM-DD -->
<!-- ### What was done -->
<!-- - Description -->
<!-- ### Files created/modified -->
<!-- - `path/to/file` -->
TEMPLATE
                    echo "  Reset: $RESET_FILE"
                    ;;
                *CHANGELOG.md)
                    cat > "$TEMP_DIR/$RESET_FILE" << 'TEMPLATE'
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

<!-- ## [Phase N] — YYYY-MM-DD -->
<!-- ### Added -->
<!-- - Feature description -->
TEMPLATE
                    echo "  Reset: $RESET_FILE"
                    ;;
                *)
                    echo "  Warning: No template defined for $RESET_FILE — skipping"
                    ;;
            esac
        else
            echo "  Warning: $RESET_FILE not found in tracked files — skipping"
        fi
    done
    echo ""
fi

# Validation pass — check for any remaining private terms
echo "--- Validation pass ---"
VALIDATION_FAILED=false
for i in $(seq 0 $((NUM_RULES - 1))); do
    FIND_TERM=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['scrub_rules'][$i]['find'])")

    # Search for remaining matches (case-sensitive)
    REMAINING=$(grep -rl "$FIND_TERM" "$TEMP_DIR" 2>/dev/null || true)
    if [ -n "$REMAINING" ]; then
        echo "  FAIL: '$FIND_TERM' still found in:"
        while IFS= read -r file; do
            REL_PATH="${file#$TEMP_DIR/}"
            echo "    $REL_PATH:"
            grep -n "$FIND_TERM" "$file" | head -5 | while IFS= read -r line; do
                echo "      $line"
            done
        done <<< "$REMAINING"
        VALIDATION_FAILED=true
    fi
done

if $VALIDATION_FAILED; then
    echo ""
    echo "ERROR: Validation failed — private terms still present after scrubbing."
    echo "Update .devax-publish.json scrub_rules to cover these cases."
    exit 1
fi
echo "  All scrub rules validated — no private terms found"
echo ""

# Blocklist validation — catch terms that scrub rules don't handle
if [ "$NUM_BLOCKLIST" -gt 0 ]; then
    echo "--- Blocklist validation ---"
    for i in $(seq 0 $((NUM_BLOCKLIST - 1))); do
        BLOCK_TERM=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['validation_blocklist'][$i])")

        REMAINING=$(grep -rl "$BLOCK_TERM" "$TEMP_DIR" 2>/dev/null || true)
        if [ -n "$REMAINING" ]; then
            echo "  FAIL: Blocklist term '$BLOCK_TERM' found in:"
            while IFS= read -r file; do
                REL_PATH="${file#$TEMP_DIR/}"
                echo "    $REL_PATH:"
                grep -n "$BLOCK_TERM" "$file" | head -3 | while IFS= read -r line; do
                    echo "      $line"
                done
            done <<< "$REMAINING"
            VALIDATION_FAILED=true
        fi
    done

    if $VALIDATION_FAILED; then
        echo ""
        echo "ERROR: Blocklist validation failed — forbidden terms found in output."
        echo "Either genericize the source files or add scrub rules to handle these."
        exit 1
    fi
    echo "  All blocklist terms validated — none found"
    echo ""
fi

# Dry-run: show diff and exit
if $DRY_RUN; then
    echo "=== DRY RUN — Diff preview ==="
    echo ""

    HAS_CHANGES=false
    cd "$REPO_ROOT"
    while IFS= read -r file; do
        if [ -f "$TEMP_DIR/$file" ]; then
            DIFF_OUTPUT=$(diff -u "$file" "$TEMP_DIR/$file" 2>/dev/null || true)
            if [ -n "$DIFF_OUTPUT" ]; then
                echo "--- $file ---"
                echo "$DIFF_OUTPUT"
                echo ""
                HAS_CHANGES=true
            fi
        fi
    done < <(git ls-files)

    if ! $HAS_CHANGES; then
        echo "(No differences — local files already match sanitized output)"
    fi

    echo ""
    echo "=== DRY RUN complete. Run without --dry-run to push. ==="
    exit 0
fi

# Live mode: init git repo in temp dir, commit, and force-push
echo "--- Pushing to $REMOTE/$BRANCH ---"
cd "$TEMP_DIR"
git init -q
git checkout -q -b "$BRANCH"
git add -A
git commit -q -m "Publish sanitized devax

Automated by scripts/publish.sh"

git remote add publish "$REMOTE_URL"
git push -f publish "$BRANCH"

echo ""
echo "=== Published successfully to $REMOTE_URL ($BRANCH) ==="
