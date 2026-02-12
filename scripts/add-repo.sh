#!/bin/bash
# Add a new repository to the planning repo
# Usage: ./scripts/add-repo.sh <portfolio> <repo-url> [local-name]
# Example: ./scripts/add-repo.sh work git@github.com:org/repo.git my-project

set -e

PORTFOLIO=$1
REPO_URL=$2
LOCAL_NAME=$3

# Read portfolio names from .devax.json if it exists, else use defaults
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../.devax.json"
if [ -f "$CONFIG_FILE" ] && command -v python3 &>/dev/null; then
    PORTFOLIOS=$(python3 -c "import json; print('|'.join(json.load(open('$CONFIG_FILE')).get('portfolios', ['work','personal','explore','infra'])))")
else
    PORTFOLIOS="work|personal|explore|infra"
fi

if [ -z "$PORTFOLIO" ] || [ -z "$REPO_URL" ]; then
    echo "Usage: $0 <portfolio> <repo-url> [local-name]"
    echo "  portfolio: ${PORTFOLIOS//|/, }"
    echo "  repo-url: git clone URL"
    echo "  local-name: optional local directory name"
    exit 1
fi

# Validate portfolio
if [[ ! "$PORTFOLIO" =~ ^(${PORTFOLIOS})$ ]]; then
    echo "Error: portfolio must be one of: ${PORTFOLIOS//|/, }"
    exit 1
fi

# Extract repo name from URL if not provided
if [ -z "$LOCAL_NAME" ]; then
    LOCAL_NAME=$(basename "$REPO_URL" .git)
fi

TARGET_DIR="$PORTFOLIO/$LOCAL_NAME"

# Check if directory already exists
if [ -d "$TARGET_DIR" ]; then
    echo "Error: $TARGET_DIR already exists"
    exit 1
fi

# Clone the repository
echo "Cloning $REPO_URL into $TARGET_DIR..."
git clone "$REPO_URL" "$TARGET_DIR"

# Add to .gitignore
IGNORE_ENTRY="$TARGET_DIR/"
if ! grep -qxF "$IGNORE_ENTRY" .gitignore 2>/dev/null; then
    echo "$IGNORE_ENTRY" >> .gitignore
    git add .gitignore
    git commit -m "Ignore $TARGET_DIR"
    echo "Added $TARGET_DIR to .gitignore and committed"
else
    echo "$TARGET_DIR already in .gitignore"
fi

echo "Done! Repository cloned to $TARGET_DIR"
