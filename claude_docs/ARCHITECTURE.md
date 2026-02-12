# Devax — Architecture

> System design, workspace organization, and infrastructure topology.
>
> **Status:** Active.

---

## System Overview

Devax is a development environment system that organizes projects into portfolio directories and provides automation via Claude Code skills. It lives in `infra/devax/` as an independent git repo and installs to the container root via symlinks.

```
workspace/                           # Container root (planning repo)
├── .claude/skills/ → devax          # Symlinked from infra/devax/
├── scripts/ → devax                 # Symlinked from infra/devax/
├── templates/ → devax               # Symlinked from infra/devax/
├── CLAUDE.md                        # Container guidance (points to Devax)
├── docs/                            # Container-specific docs (not Devax)
├── work/                            # Work projects portfolio
├── personal/                        # Personal projects
├── explore/                         # Third-party exploration
└── infra/
    └── devax/                       # Devax system (this repo)
        ├── .claude/skills/          # Claude Code skills
        ├── scripts/                 # Workspace utilities
        ├── templates/               # Project templates
        └── claude_docs/             # Devax evolution tracking
```

---

## Key Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Installation method | Symlink-based | Container root stays minimal; Devax versioned independently |
| Workspace structure | Portfolio-based organization | Separates work, personal, exploration, and infrastructure projects while maintaining git independence |
| Documentation pattern | 8-doc structure | Standardized docs across all projects with clear update triggers |
| Skills system | Symlinked to .claude/skills/ | Skills available to all projects (/scaffold-docs, /deploy, /wrap-session, etc.) |
| Git strategy | Devax is its own repo | Devax can be forked/shared; container root has its own git |
| Credential scoping | By portfolio directory | Work credentials in work/, personal credentials in personal/, etc. |

---

## Infrastructure

### Symlink Installation
- `.claude/skills/` → `infra/devax/.claude/skills/`
- `scripts/` → `infra/devax/scripts/`
- `templates/` → `infra/devax/templates/`

### Shared Tooling
- **Scripts:** `scripts/add-repo.sh`, `scripts/dev-updates/` (Slack integration)
- **Documentation templates:** `templates/INFRASTRUCTURE.md`, `templates/PROJECT-CLAUDE-TEMPLATE.md`
- **Skills:** 5 workspace-level skills for documentation and deployment automation
