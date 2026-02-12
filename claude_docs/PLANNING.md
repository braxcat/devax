# Devax — Planning

> Future features, research findings, reference materials, and open questions.
>
> **Last updated:** 2026-02-11

## 1. Open Questions

- How should we handle MCP server configurations across projects?
- What's the best way to share environment variable patterns across projects?

---

## 2. Future Workspace Improvements

### Slack Integration Setup
- Create Slack app and bot token
- Configure channels in `scripts/dev-updates/config.json`
- Run channel setup script
- Test posting workflow

### Additional Portfolio Categories
Consider if we need:
- `archive/` — Deprecated or completed projects
- `client/` — Client-specific work (if applicable)
- `research/` — Deep research projects separate from exploration

---

## 3. Research & References

### claude-project-kit (upstream)
- Devax is a fork/evolution of the claude-project-kit project
- Key patterns adopted:
  - Portfolio organization
  - 8-file documentation structure
  - Claude Code skills
  - Slack integration scripts

### Documentation Standards
- Keep a Changelog: https://keepachangelog.com/en/1.1.0/
- Markdown CommonMark spec for consistency

---

## 4. Workflow Improvements

### Cross-Project Automation Ideas
- Script to run health checks across all work/ projects
- Unified deployment dashboard
- Dependency update checker across repos
- Standardized .env template generator

### Future Projects to Build
- Automation for syncing credentials securely
- Workspace backup script
- Project scaffolding wizard
- Cross-repo search tool
