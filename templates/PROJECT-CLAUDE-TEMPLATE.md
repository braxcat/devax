# [Project Name]

Brief description of what this project does.

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

### Post-Deploy Checklist

After deploying a new phase, run `/devax-deploy` or manually:
1. Update `claude_docs/CHANGELOG.md`, `claude_docs/ROADMAP.md`, `claude_docs/FEATURES.md` (per table above)
2. Run `/devax-post-update all` to post progress to Slack

## Quick Start

### Prerequisites
- List required tools/versions

### Installation
```bash
# Installation commands
```

### Development Commands
| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |

## Configuration

### Required Environment Variables
| Variable | Description |
|----------|-------------|
| `API_KEY` | Description of this key |

## Architecture

```
src/
├── components/     # UI components
├── lib/            # Shared utilities
└── pages/          # Route handlers
```

## Deployment

See also: [INFRASTRUCTURE.md](INFRASTRUCTURE.md) for shared GCP patterns.

| Resource | Value |
|----------|-------|
| GCP Project | `project-id` |
| Cloud Run URL | `https://...run.app` |
| Cloud SQL Instance | `instance-name` |
| Database name | `db_name` |

### Deploy
```bash
gcloud builds submit --config=cloudbuild.yaml --project=PROJECT_ID
```

### Migrations
```bash
cloud-sql-proxy PROJECT:REGION:INSTANCE --port PORT
DATABASE_URL="postgresql://user:pass@localhost:PORT/db_name" npx prisma migrate deploy
```

## Key Patterns

- **Pattern 1:** Description
- **Pattern 2:** Description

## Component Responsibilities

### ComponentName (path/to/file.ts)
- What it does
- Key behaviors
