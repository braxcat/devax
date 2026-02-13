---
name: bosun-post-update
description: Post business progress updates to Slack (roadmap, releases, changelog, stats, confluence). Use when user asks to share business progress or post to Slack.
---

Post business progress updates to Slack using the dev-updates framework with Bosun config.

## Usage
- `/bosun-post-update roadmap` — Post roadmap progress to #bosun-roadmap
- `/bosun-post-update release` — Post latest release to #bosun-releases
- `/bosun-post-update changelog` — Post latest changelog to #bosun-changelog
- `/bosun-post-update stats` — Post coding stats to #coding-stats-new (excludes confluence .md churn)
- `/bosun-post-update confluence` — Post Confluence sync status to #bosun-confluence
- `/bosun-post-update all` — Post all five

## How it works
1. First run with `--dry-run` to preview the message
2. Show the preview to the user
3. If they approve, run without `--dry-run` to post

## Commands
Script: `scripts/dev-updates/dev_updates.py`
Config: `scripts/dev-updates/config-bosun.json`

Always use `--config scripts/dev-updates/config-bosun.json` to route to Bosun channels.

Requires `SLACK_BOT_TOKEN` env var.

## Examples

```bash
# Preview roadmap post
python3 scripts/dev-updates/dev_updates.py roadmap --dry-run --config scripts/dev-updates/config-bosun.json

# Preview confluence status
python3 scripts/dev-updates/dev_updates.py confluence --dry-run --config scripts/dev-updates/config-bosun.json

# Post all updates
python3 scripts/dev-updates/dev_updates.py all --config scripts/dev-updates/config-bosun.json

# Post with wrap context (session wrap headings)
python3 scripts/dev-updates/dev_updates.py all --config scripts/dev-updates/config-bosun.json --context wrap

# Setup channels (one-time)
python3 scripts/dev-updates/dev_updates.py setup-channels --config scripts/dev-updates/config-bosun.json
```

## Channels

| Channel | Content |
|---------|---------|
| `bosun-changelog` | Business changes (doc updates, decisions, strategy shifts) |
| `bosun-releases` | Business releases (Confluence publishes, product milestones) |
| `bosun-roadmap` | Business roadmap progress |
| `bosun-confluence` | Confluence sync activity and page stats |
| `coding-stats-new` | Code commits (shared with devax, excludes confluence .md changes) |
