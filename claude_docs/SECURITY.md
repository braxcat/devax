# Devax — Security

> Data classification, credential scoping, and security practices for the workspace.
>
> **Status:** Initial draft. Security practices being established.

## Credential Scoping

Credentials are scoped by portfolio directory to prevent accidental cross-contamination:

| Portfolio | Credential Scope | Storage Location |
|-----------|-----------------|------------------|
| **work/** | Work project credentials (GCP, databases, API keys) | `.env` files within each work/ project |
| **personal/** | Personal project credentials | `.env` files within each personal/ project |
| **expl/** | Third-party service credentials for learning | `.env` files within each expl/ project |
| **infra/** | Infrastructure tooling credentials | `.env` files within each infra/ project |

**Important:** Never commit `.env` files. All portfolios' `.gitignore` files should include `*.env`.

---

## Secrets Management

### Workspace-Level
- **Slack Bot Tokens:** Stored in `scripts/dev-updates/config.json` (gitignored)
- **MCP Servers:** Credentials stored in `.claude.json` or environment-specific configs

### Project-Level
Each project manages its own secrets following its own security requirements.

**Best practices:**
- Use GCP Secret Manager for production secrets (work/ projects)
- Document secret requirements in project CLAUDE.md
- Never commit credentials, tokens, or API keys
- Use `.env.template` files to document required variables

---

## Access Control

### Workspace Files
- `.claude/` — Contains skills accessible to all projects (symlinked from Devax)
- `scripts/` — Helper scripts; some may require credentials to execute (symlinked from Devax)
- `templates/` — Templates and documentation (public, symlinked from Devax)

### Portfolio Access
- Each portfolio's projects are independent
- No shared credentials between portfolios by default
- Credentials must be explicitly copied/configured per project

---

## Known Gaps & TODOs

- [ ] Establish workspace-level secret scanning (pre-commit hooks?)
- [ ] Document credential rotation procedures
- [ ] Review and audit all project .gitignore files for secret patterns
- [ ] Create secure credential template generator for new projects
