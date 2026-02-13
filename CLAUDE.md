# Devax — Development Environment System

Development environment system providing portfolio organization, automation skills, and workflow tools.

## What is Devax?

Devax is a comprehensive development environment system that:
- Organizes projects into portfolios (work/, personal/, expl/, infra/)
- Provides Claude Code skills for automation
- Standardizes documentation across projects
- Evolves your development practices

## Installation

To install Devax in a container environment:

1. Clone this repo to `infra/devax/`
2. Symlink skills, scripts, and templates to container root:
   ```bash
   cd /path/to/container
   ln -s /path/to/container/infra/devax/.claude/skills .claude/skills
   ln -s /path/to/container/infra/devax/scripts scripts
   ln -s /path/to/container/infra/devax/templates templates
   ```
3. Set your commit co-author branding. Add to your container root `CLAUDE.md`:

   ## Commit Conventions
   All commits must use: Co-Authored-By: <Your Name>'s Devax using Claude <model> <noreply@anthropic.com>

## Documentation Index

| Document | Purpose | Update when... |
|----------|---------|----------------|
| claude_docs/ARCHITECTURE.md | Devax system architecture | Architectural changes |
| claude_docs/CHANGELOG.md | Devax change history | After updates |
| claude_docs/FEATURES.md | Capabilities and tools | New skills or tools added |
| claude_docs/PLANNING.md | Future improvements | New ideas or research |
| claude_docs/ROADMAP.md | Devax evolution phases | Planning or completing phases |
| claude_docs/SECURITY.md | Credential scoping | Security changes |
| claude_docs/TESTING.md | Validation procedures | Testing approach changes |
| claude_docs/WORKLOG.md | Session log | After each session |

## Skills Provided

### Development Skills

| Skill | Description |
|-------|-------------|
| `/devax-scaffold-docs` | Create `claude_docs/` structure in any project |
| `/devax-deploy` | Deploy to GCP Cloud Run + update docs + post to Slack |
| `/devax-wrap-session` | End-of-session cleanup — docs + commit + push + memory + Slack |
| `/devax-update-docs` | Update documentation after work session (no deploy) |
| `/devax-post-update` | Post progress updates to Slack channels |
| `/devax-publish` | Publish sanitized devax to public repo |
| `/devax-code-review` | Comprehensive code review (8 quality + 4 security categories) |
| `/devax-stats` | Project statistics and dev metrics (codebase, git, time estimate) |

<!-- BUSINESS:START -->
### Business Skills (Bosun)

| Skill | Description |
|-------|-------------|
| `/bosun-scaffold` | Create `docs/business/` structure with business claude_docs/ |
| `/bosun-confluence-push` | Push local markdown changes to Confluence wiki |
| `/bosun-confluence-pull` | Pull latest pages from Confluence to local mirror |
| `/bosun-post-update` | Post business progress to Slack (roadmap, releases, changelog, stats, confluence) |
| `/bosun-wrap-session` | End-of-session cleanup for business work |
<!-- BUSINESS:END -->

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/dev-updates/` | Slack posting (dev_updates.py + lib/) |
| `scripts/add-repo.sh` | Add new project repos to portfolios |
| `scripts/publish.sh` | Publish sanitized devax to public repo |

## Templates

| Template | Purpose |
|----------|---------|
| templates/INFRASTRUCTURE.md | Shared infrastructure patterns |
| templates/PROJECT-CLAUDE-TEMPLATE.md | Project CLAUDE.md template |

## Portfolio Organization

Devax organizes projects into portfolios:

| Portfolio | Purpose |
|-----------|---------|
| `work/` | Work projects |
| `personal/` | Personal projects |
| `expl/` | Third-party repos for exploration |
| `infra/` | Infrastructure projects (including Devax itself) |

## Adding New Projects

```bash
./scripts/add-repo.sh <portfolio> <repo-url> [local-name]
# Example: ./scripts/add-repo.sh work git@github.com:org/repo.git my-project
```
