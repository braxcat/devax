# Devax — Features

> Complete inventory of Devax capabilities and tools.
>
> **Last updated:** 2026-02-13

---

## Portfolio Organization

**What it does:** Organizes projects into context-specific directories

**Portfolios:**
- `work/` — Work projects
- `personal/` — Personal projects
- `expl/` — Third-party repos for exploration and learning
- `infra/` — Infrastructure, DevOps, shared tooling (including Devax itself)

**Key benefit:** Each portfolio contains fully independent git repositories with separate histories, branches, and remotes

---

## Claude Code Skills — Development

**What it does:** Custom slash commands for development workflows

**Available skills:**
- `/devax-scaffold-docs` — Create standardized claude_docs/ structure in any project
- `/devax-deploy` — Deploy to GCP Cloud Run + update docs + post to Slack
- `/devax-update-docs` — Update docs after a work session (no deploy needed)
- `/devax-wrap-session` — End-of-session cleanup (docs + commit + push + memory + Slack)
- `/devax-post-update` — Post progress updates to Slack channels
- `/devax-publish` — Publish sanitized devax to public repo

**Location:** `.claude/skills/` (symlinked from `infra/devax/.claude/skills/`)

---

<!-- BUSINESS:START -->
## Claude Code Skills — Business (Bosun)

**What it does:** Custom slash commands for business operations, branded as Bosun (aka Boats)

**Available skills:**
- `/bosun-scaffold` — Create `docs/business/` workspace with 8 business orientation files
- `/bosun-confluence-push` — Push local markdown changes to Confluence wiki
- `/bosun-confluence-pull` — Pull latest Confluence pages to local mirror
- `/bosun-post-update` — Post business progress to Slack (roadmap, releases, changelog, stats, confluence)
- `/bosun-wrap-session` — End-of-session cleanup for business work (docs + Confluence + commit + memory + Slack)

**Location:** `.claude/skills/` (same directory, excluded from public publish)

**Slack channels:** `bosun-roadmap`, `bosun-releases`, `bosun-changelog`, `bosun-confluence`, `coding-stats-new` (shared)
<!-- BUSINESS:END -->

---

## Shared Documentation Templates

**What it does:** Provides templates for new projects and shared infrastructure patterns

**Templates:**
- `templates/INFRASTRUCTURE.md` — Shared infrastructure patterns, deploy commands, secrets
- `templates/PROJECT-CLAUDE-TEMPLATE.md` — Template for new project CLAUDE.md files

---

## Workspace Utilities

**What it does:** Helper scripts for common workspace operations

**Scripts:**
- `scripts/add-repo.sh` — Add new repository to a portfolio (reads portfolio names from `.devax.json`, defaults to work/personal/explore/infra)
- `scripts/publish.sh` — Sanitize and push devax to public repo (scrub rules, exclude paths, BUSINESS stripping, blocklist validation)
- `scripts/dev-updates/` — Slack integration for posting updates, roadmaps, and stats

## Documentation Standards

**What it does:** Standardized 8-file documentation structure for consistent project documentation

**Structure:**
- ARCHITECTURE.md — System design, schema, infrastructure
- CHANGELOG.md — Release history
- FEATURES.md — Feature inventory
- PLANNING.md — Future features, research, references
- ROADMAP.md — Phase plan with status tracking
- SECURITY.md — Data classification, encryption, auth
- TESTING.md — Test strategy and coverage targets
- WORKLOG.md — Development session log

---


---

## Symlink-Based Installation

**What it does:** Installs Devax to a container environment via symlinks, keeping the system versioned independently

**What gets linked:**
- `.claude/skills/` → `infra/devax/.claude/skills/`
- `scripts/` → `infra/devax/scripts/`
- `templates/` → `infra/devax/templates/`

**Key benefit:** Devax can be updated, versioned, and shared independently while container root stays minimal
