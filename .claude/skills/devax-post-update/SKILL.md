---
name: devax-post-update
description: Post project progress updates to Slack (roadmap, releases, changelog, stats). Use when user asks to share progress or post to Slack.
---

Post progress updates to Slack using the dev-updates framework.

## Usage
- `/devax-post-update roadmap` — Post roadmap progress to #dev-roadmap
- `/devax-post-update release` — Post latest release to #dev-releases
- `/devax-post-update changelog` — Post latest changelog to #dev-changelog
- `/devax-post-update stats` — Post coding stats to #coding-stats
- `/devax-post-update all` — Post all four

## How it works
1. First run with `--dry-run` to preview the message
2. Show the preview to the user
3. If they approve, run without `--dry-run` to post

## Commands
Script: `scripts/dev-updates/dev_updates.py`

The script needs a config.json or `--repo` and `--project` flags.
Check if a config.json exists in the current project's directory first.
If not, use `--repo` pointing to the project root and `--project` with the project name.

Requires `SLACK_BOT_TOKEN` env var.

## Examples

```bash
# Preview roadmap post
python3 scripts/dev-updates/dev_updates.py roadmap --dry-run --repo /path/to/repo --project "Project Name"

# Post all updates
python3 scripts/dev-updates/dev_updates.py all --repo /path/to/repo --project "Project Name"

# Setup channels (one-time)
python3 scripts/dev-updates/dev_updates.py setup-channels
```
