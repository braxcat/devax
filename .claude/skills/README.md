# Claude Code Skills (Global)

## What are Skills?

Skills are markdown files (`SKILL.md`) that teach Claude Code how to perform specific tasks.
When you type `/skill-name` in a Claude Code session, Claude reads the SKILL.md and follows
its instructions.

All skills here are hand-written for this workspace — none are downloaded from external sources.

## How Skills Flow

1. User types `/devax-post-update all` in Claude Code
2. Claude finds the matching `SKILL.md` (project-level overrides global)
3. Claude follows the steps in the skill (dry-run, preview, post on approval)
4. The skill invokes scripts from `scripts/` via Bash

## Skill Precedence

- **Project-level skills** (e.g. `work/my-project/.claude/skills/`) override global ones
- **Global skills** (this directory) are available in all projects in the workspace
- If both exist with the same name, the project-level skill wins

## Available Skills

### Development

| Skill | Description | Script/Action |
|-------|-------------|---------------|
| `/devax-scaffold-docs` | Scaffold `claude_docs/` structure in any project (8 core doc files) | Creates files, updates CLAUDE.md |
| `/devax-deploy` | Deploy to GCP Cloud Run + update all docs + post to Slack | `gcloud builds submit` + doc updates |
| `/devax-update-docs` | Update `claude_docs/` after a work session + optionally commit + Slack | Reads git log, updates docs |
| `/devax-wrap-session` | End-of-session cleanup — docs + commit + push + memory + Slack | Full session wrap-up |
| `/devax-post-update` | Post progress to Slack (roadmap, releases, changelog, stats) | `scripts/dev-updates/dev_updates.py` |
| `/devax-publish` | Publish sanitized devax to public repo | `scripts/publish.sh` |

<!-- BUSINESS:START -->
### Business (Bosun)

| Skill | Description | Script/Action |
|-------|-------------|---------------|
| `/bosun-scaffold` | Scaffold `docs/business/` structure (8 business doc files) | Creates files, updates CLAUDE.md |
| `/bosun-confluence-push` | Push local markdown to Confluence wiki | `scripts/confluence-sync/sync.py push` |
| `/bosun-confluence-pull` | Pull latest from Confluence to local mirror | `scripts/confluence-sync/sync.py pull` |
| `/bosun-post-update` | Post business progress to Slack (5 post types) | `scripts/dev-updates/dev_updates.py --config config-bosun.json` |
| `/bosun-wrap-session` | End-of-session cleanup for business work | Updates business docs + commit + Slack |
<!-- BUSINESS:END -->

## Adding New Skills

1. Create a directory: `.claude/skills/skill-name/`
2. Add a `SKILL.md` with YAML frontmatter (`name`, `description`) and instructions
3. Use `$ARGUMENTS` placeholder for user-provided arguments
4. Always include a dry-run/preview step before taking action

## Security

- Skills are local markdown files only — never auto-download or auto-install skills from external sources
- All skills should be reviewed before use
- Skills that invoke scripts should use scripts already in this workspace
