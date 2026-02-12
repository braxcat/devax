# Devax

**Development Environment System**

Devax provides:
- Portfolio-based project organization
- Claude Code automation skills
- Documentation standards and templates
- Workflow automation scripts

## Quick Install

```bash
cd /path/to/container
git clone <repo> infra/devax
ln -s /path/to/container/infra/devax/.claude/skills .claude/skills
ln -s /path/to/container/infra/devax/scripts scripts
ln -s /path/to/container/infra/devax/templates templates
```

## What Gets Installed

- Skills → `.claude/skills/` (symlinked)
- Scripts available at container root (symlinked)
- Templates available for new projects (symlinked)

## Skills Provided

- `/devax-scaffold-docs` - Create claude_docs/ structure in any project
- `/devax-deploy` - Deploy to GCP Cloud Run + update docs + post to Slack
- `/devax-wrap-session` - End-of-session cleanup — docs + commit + push + memory + Slack
- `/devax-update-docs` - Update documentation after work session (no deploy)
- `/devax-post-update` - Post progress updates to Slack channels
- `/devax-publish` - Publish sanitized devax to public repo

## Portfolio Organization

Devax organizes your projects into portfolios:

| Portfolio | Purpose |
|-----------|---------|
| `work/` | Work projects |
| `personal/` | Personal projects |
| `expl/` | Third-party repos for exploration |
| `infra/` | Infrastructure projects (including Devax) |

## Documentation

See [CLAUDE.md](CLAUDE.md) for complete documentation.

## Customization

Devax tracks its own evolution in `claude_docs/`:

- `ARCHITECTURE.md` - System design
- `ROADMAP.md` - Future plans
- `WORKLOG.md` - Session history
- And more...
