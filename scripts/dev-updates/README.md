# Dev Updates — Slack Progress Poster

Post project progress updates to Slack from markdown files (ROADMAP.md, CHANGELOG.md, FEATURES.md) and coding stats from git history.

## Prerequisites

- Python 3.9+
- A Slack App with required Bot Token scopes (see below)
- `SLACK_BOT_TOKEN` environment variable set to the Bot User OAuth Token (`xoxb-...`)

No third-party dependencies — uses Python stdlib only.

## Setup

### 1. Slack App — Required Bot Token Scopes

Add these scopes to your Slack App under **OAuth & Permissions → Bot Token Scopes**:

| Scope | Purpose |
|-------|---------|
| `chat:write` | Post messages to channels |
| `channels:manage` | Create public channels |
| `channels:join` | Join channels the bot creates |
| `channels:read` | List channels to check existence |
| `channels:history` | Read channel history (for delete) |
| `users:read` | List workspace members (for invites) |

**Reinstall required** after adding scopes (Install App → Reinstall to Workspace).

### 2. Environment

```bash
export SLACK_BOT_TOKEN='xoxb-your-token-here'
```

### 3. Create channels (one-time)

```bash
python3 dev_updates.py setup-channels --config config.json
```

This creates `#dev-roadmap`, `#dev-releases`, `#dev-changelog`, and `#coding-stats` (or your configured names).

## Usage

```bash
# Preview what would be posted (no Slack API calls)
python3 dev_updates.py roadmap --dry-run --repo /path/to/repo --project "My Project"

# Post roadmap progress
python3 dev_updates.py roadmap --repo /path/to/repo --project "My Project"

# Post latest release notes
python3 dev_updates.py release --repo /path/to/repo --project "My Project"

# Post latest changelog entry
python3 dev_updates.py changelog --repo /path/to/repo --project "My Project"

# Post coding stats (LoC, commits, charts, dev time estimate)
python3 dev_updates.py stats --repo /path/to/repo --project "My Project"

# Post coding stats without charts
python3 dev_updates.py stats --no-charts --repo /path/to/repo --project "My Project"

# Post all four
python3 dev_updates.py all --repo /path/to/repo --project "My Project"

# Replay full history (one post per phase, oldest first)
python3 dev_updates.py replay --repo /path/to/repo --project "My Project"

# Replay specific type only
python3 dev_updates.py replay --type roadmap --repo /path/to/repo --project "My Project"

# Replay stats (one post per dev day)
python3 dev_updates.py replay --type stats --repo /path/to/repo --project "My Project"

# Delete last N bot messages from all channels
python3 dev_updates.py delete-last 3

# Delete from specific channel
python3 dev_updates.py delete-last 1 --channel dev-roadmap

# Delete ALL bot messages from all channels (use before full replay)
python3 dev_updates.py clear-all

# Multi-repo stats (tags commits by project)
python3 dev_updates.py stats --repo /path/to/project --repo /path/to/workspace --project "My Project"

# Output parsed data as JSON (for debugging)
python3 dev_updates.py roadmap --json --repo /path/to/repo
```

### Using a config file

Instead of passing `--repo` and `--project` every time:

```bash
cp config.example.json config.json
# Edit config.json with your values
python3 dev_updates.py roadmap --dry-run
```

## Expected file structure in repo

The script expects these files in the repo:

| File | Used by | Required |
|------|---------|----------|
| `claude_docs/ROADMAP.md` | `roadmap`, `replay` | Yes (for roadmap) |
| `claude_docs/CHANGELOG.md` | `release`, `changelog`, `replay` | Yes (for release/changelog) |
| `claude_docs/FEATURES.md` | `release` (platform stats) | Optional |
| Git history | `stats`, `replay --type stats` | Yes (for stats) |

The `stats` command imports `scripts/coding-stats/` as a library — it must be present as a sibling directory.

### ROADMAP.md format

Must have a Phase Summary table:

```markdown
## Phase Summary

| Phase | Name | Date | Status |
|-------|------|------|--------|
| 1 | Foundation | 2026-02-08 | COMPLETE |
| 2 | Features | 2026-02-09 | PENDING |
```

### CHANGELOG.md format

Follows [Keep a Changelog](https://keepachangelog.com/):

```markdown
## [Phase 2] — 2026-02-09
### Added
- Feature one
- Feature two
### Fixed
- Bug fix
```

## How it works

1. **Parsers** (`lib/parsers.py`) read markdown files and extract structured data
2. **Formatters** (`lib/formatters.py`) convert data into Slack Block Kit JSON
3. **Slack client** (`lib/slack_client.py`) posts via the Slack Web API using Bot Token auth
4. **Coding stats** — imported from sibling `scripts/coding-stats/` (git analysis, charts via QuickChart.io, COCOMO estimates)
5. **CLI** (`dev_updates.py`) ties it all together with argparse

Dates are displayed in `Feb 8` format (not `2026-02-08`) for international clarity.

## Channels

| Channel | Post type | Content |
|---------|-----------|---------|
| `#dev-roadmap` | `roadmap` | Phase completion status with progress bar |
| `#dev-releases` | `release` | Latest shipped phase with feature list |
| `#dev-changelog` | `changelog` | Detailed changelog entry (Added/Fixed/Changed) |
| `#coding-stats` | `stats` | LoC, commits, charts, dev time estimate (from `scripts/coding-stats/`) |

## Claude Code Integration

A `/devax-post-update` slash command is available in Claude Code sessions:

```
/devax-post-update roadmap    — Post roadmap to #dev-roadmap
/devax-post-update release    — Post latest release to #dev-releases
/devax-post-update changelog  — Post latest changelog to #dev-changelog
/devax-post-update stats      — Post coding stats to #coding-stats
/devax-post-update all        — Post all four
```

The skill previews with `--dry-run` first, then posts on approval. Requires `SLACK_BOT_TOKEN` in the environment.

Skill definition: `.claude/skills/devax-post-update/SKILL.md`.
