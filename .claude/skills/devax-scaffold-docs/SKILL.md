---
name: devax-scaffold-docs
description: Scaffold the standard claude_docs/ documentation structure in any project. Creates missing doc files, updates CLAUDE.md Documentation Index, and flags redundant files for cleanup.
---

Scaffold the `claude_docs/` documentation structure for a project.

## Usage
- `/devax-scaffold-docs` — Run in the current project directory

## What it does

1. **Create `claude_docs/` directory** if it doesn't exist
2. **Create missing core doc files** from the templates below (skip files that already exist)
3. **Ensure CLAUDE.md has a Documentation Index** table pointing to all 8 docs
4. **Ensure README.md has a Documentation section** linking to key docs
5. **Cleanup review** — scan for files that may be duplicates of content now in `claude_docs/`:
   - `CHANGELOG.md` at project root (now in `claude_docs/`)
   - `WORKLOG.md` at project root (now in `claude_docs/`)
   - `docs/` directory (now replaced by `claude_docs/`)
   - `docs/future/`, `docs/research/`, `docs/reference/` (now consolidated in `claude_docs/PLANNING.md`)
   - Any `*-architecture.md` files (now `claude_docs/ARCHITECTURE.md`)
   - List these files and ask: "These files appear to be duplicates of content now in claude_docs/ — delete them?"
   - Only delete after user confirms
6. **Report** what was created, skipped (already exists), and flagged for deletion

## Core doc files (8 required)

Create any that are missing. Do NOT overwrite existing files.

### claude_docs/ARCHITECTURE.md
```markdown
# [Project Name] — Architecture

> System design, schema, data flow, and infrastructure topology.
>
> **Status:** Initial draft.

---

## System Overview

TODO: Add system architecture diagram and description.

---

## Database Schema

TODO: Add key models and relationships.

---

## Key Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| | | |
```

### claude_docs/CHANGELOG.md
```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

<!-- ## [Phase N] — YYYY-MM-DD -->
<!-- ### Added -->
<!-- - Feature description -->
```

### claude_docs/FEATURES.md
```markdown
# [Project Name] — Features

> Complete inventory of user-facing features.
>
> **Last updated:** [date]

---

TODO: Add feature sections with routes and descriptions.
```

### claude_docs/PLANNING.md
```markdown
# [Project Name] — Planning

> Future features, research findings, reference materials, and open questions.
>
> **Last updated:** [date]

---

## 1. Open Questions

- TODO: Add open questions and future feature ideas
```

### claude_docs/ROADMAP.md
```markdown
# [Project Name] — Roadmap

> Phase plan with status tracking.
>
> **Last updated:** [date]

---

## Phase Summary

| Phase | Name | Date | Status |
|-------|------|------|--------|
| 1 | Foundation | — | PENDING |
```

### claude_docs/SECURITY.md
```markdown
# [Project Name] — Security

> Data classification, encryption, authentication, and compliance.
>
> **Status:** Initial draft. Full security audit pending.

---

## Data Classification

| Classification | Fields | Storage | Display |
|---------------|--------|---------|---------|-
| **Sensitive PII** | | | |
| **Personal** | | | |
| **Internal** | | | |
| **Public** | | | |

---

## Authentication

TODO: Describe auth model.

---

## Known Gaps & TODOs

- [ ] Full security audit needed before public launch
```

### claude_docs/TESTING.md
```markdown
# [Project Name] — Testing

> Test strategy, stack, coverage targets, and priority modules.
>
> **Status:** Planned. No tests written yet.

---

## Test Stack

| Tool | Purpose |
|------|---------|
| Vitest | Unit + integration tests |
| Playwright | E2E tests |

---

## Priority Modules

TODO: List modules to test in priority order.
```

### claude_docs/WORKLOG.md
```markdown
# [Project Name] — Work Log

> Development session log. Updated after each work session.

---

<!-- ## Session: YYYY-MM-DD -->
<!-- ### What was done -->
<!-- - Description -->
<!-- ### Files created/modified -->
<!-- - `path/to/file` -->
```

## Documentation Index template (for CLAUDE.md)

If CLAUDE.md doesn't have a Documentation Index table, add one after the project description:

```markdown
### Documentation Index

| Document | Purpose | Update when... |
|----------|---------|----------------|
| [README.md](README.md) | Project overview, setup, demo users | Features or stack change |
| [claude_docs/ARCHITECTURE.md](claude_docs/ARCHITECTURE.md) | System design, schema, infra | Architectural changes |
| [claude_docs/CHANGELOG.md](claude_docs/CHANGELOG.md) | Release history | After each deploy |
| [claude_docs/FEATURES.md](claude_docs/FEATURES.md) | Feature inventory (LLM reads this) | Any feature ships/changes |
| [claude_docs/PLANNING.md](claude_docs/PLANNING.md) | Future features, research, reference materials | New ideas or research |
| [claude_docs/ROADMAP.md](claude_docs/ROADMAP.md) | Phase plan + future work | Planning or completing phases |
| [claude_docs/SECURITY.md](claude_docs/SECURITY.md) | Data classification, encryption, auth, compliance | Security architecture changes |
| [claude_docs/TESTING.md](claude_docs/TESTING.md) | Test strategy, tiers, coverage targets | Test stack or strategy changes |
| [claude_docs/WORKLOG.md](claude_docs/WORKLOG.md) | Dev session log | After each session |
```

## Important

- Do NOT overwrite existing files — only create what's missing
- Replace `[Project Name]` with the actual project name from CLAUDE.md or the directory name
- Replace `[date]` with today's date
- After scaffolding, remind the user to fill in the TODO sections
