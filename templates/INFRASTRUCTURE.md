# Infrastructure — Shared Reference

Shared infrastructure reference for all projects in the workspace. Each project's CLAUDE.md should have its own `## Deployment` section with project-specific details; this doc covers the shared patterns.

## Per-Project Documentation Standard

Every project must maintain a `CLAUDE.md` at its root (see [PROJECT-CLAUDE-TEMPLATE.md](PROJECT-CLAUDE-TEMPLATE.md)). Each CLAUDE.md should include a **Documentation Index** table listing the project's key docs so Claude can find them.

### Required project docs

Only `README.md` and `CLAUDE.md` live at the project root. All other docs go in `claude_docs/`.

| Doc | Purpose | Update when... |
|-----|---------|----------------|
| `CLAUDE.md` | Project overview, stack, commands, deployment, patterns | Any architectural change |
| `claude_docs/ARCHITECTURE.md` | System design, schema, data flow, infra topology | Architectural changes |
| `claude_docs/CHANGELOG.md` | Release history (Keep a Changelog format, newest-first) | After each deploy |
| `claude_docs/FEATURES.md` | Feature inventory (LLM reads this for awareness) | Any feature ships/changes |
| `claude_docs/PLANNING.md` | Future features, research findings, reference materials | New ideas or research |
| `claude_docs/ROADMAP.md` | Phase plan with status tracking + future phases | Planning or completing phases |
| `claude_docs/SECURITY.md` | Data classification, encryption, auth, compliance | Security architecture changes |
| `claude_docs/TESTING.md` | Test strategy, stack, coverage targets, priority modules | Test infrastructure changes |
| `claude_docs/WORKLOG.md` | Dev session log (updated after each work session) | After each session |

Use `/devax-scaffold-docs` to create this structure in a new project.

### Reference doc structure

```
project/
├── README.md                    # Public-facing project overview
├── CLAUDE.md                    # Dev context for Claude (includes Documentation Index)
└── claude_docs/
    ├── ARCHITECTURE.md
    ├── CHANGELOG.md
    ├── FEATURES.md
    ├── PLANNING.md
    ├── ROADMAP.md
    ├── SECURITY.md
    ├── TESTING.md
    └── WORKLOG.md
```

### Slack channels (dev-updates tool)

Progress is posted to Slack via `scripts/dev-updates/`:

| Channel | Content | Source |
|---------|---------|--------|
| `#dev-roadmap` | Roadmap snapshots | `claude_docs/ROADMAP.md` |
| `#dev-releases` | Phase-by-phase releases | `claude_docs/CHANGELOG.md` |
| `#dev-changelog` | Phase-by-phase changelogs | `claude_docs/CHANGELOG.md` |
| `#coding-stats` | Daily git stats with tags | Git log (multi-repo) |

Post updates: `python3 scripts/dev-updates/dev_updates.py all --repo <path> --project <name>`

## GCP Account

> **Replace this section with your GCP account details.**

- **Organization:** Your Org
- **Account:** `your-email@example.com`
- **Default region:** `australia-southeast1`

## Project: example-project

> **Replace this section with your project's infrastructure details.**

| Resource | Value |
|----------|-------|
| GCP Project | `your-project-id` |
| Cloud Run URL | `https://your-service-XXXXXXXXX.REGION.run.app` |
| Cloud SQL Instance | `your-db` (Postgres 16, db-f1-micro) |
| Database name | `your_db` |
| Database user | `your_user` |
| Artifact Registry | `your-registry` |

### Secrets (GCP Secret Manager)

All secrets are in Secret Manager — never in code or env vars in Cloud Run config.

| Secret | Purpose |
|--------|---------|
| `DATABASE_URL` | Cloud SQL connection string (Unix socket) |
| `DB_PASSWORD` | Database password (for local proxy access) |
| `AUTH_SECRET` | NextAuth session signing key |
| `AUTH_URL` | NextAuth callback URL |
| `GEMINI_API_KEY` | Google Gemini LLM |

### Deploy

```bash
cd path/to/project
gcloud builds submit --config=cloudbuild.yaml --project=your-project-id
```

### Migrations (Cloud SQL via local proxy)

```bash
# Start proxy (use a unique port per project to avoid conflicts)
cloud-sql-proxy your-project-id:region:your-db --port 5434

# Get password
gcloud secrets versions access latest --secret=DB_PASSWORD --project=your-project-id

# Apply migrations
DATABASE_URL="postgresql://user:<PASSWORD>@localhost:5434/your_db?schema=public" npx prisma migrate deploy
```

### IAM

Compute Engine default SA (`XXXXXXXXX-compute@developer.gserviceaccount.com`) needs:
- `run.admin`, `iam.serviceAccountUser` (deploy to Cloud Run)
- `secretmanager.secretAccessor` (read secrets)
- `cloudsql.client` (connect to Cloud SQL)
- `storage.objectAdmin`, `iam.serviceAccountTokenCreator` (GCS signed URLs)
- `artifactregistry.writer` (push images from Cloud Build)
- `logging.logWriter`

---

## Shared Patterns

### Security

- **Never commit secrets** — use GCP Secret Manager
- **No credentials in env vars** — mount from Secret Manager in cloudbuild.yaml
- **DB passwords** — always retrieve via `gcloud secrets versions access latest`
- **ADC for local dev** — `gcloud auth application-default login` (org policy may block SA key creation)

### Cloud Build

- Pipeline defined in `cloudbuild.yaml` per project
- Uses Compute Engine default SA (not Cloud Build SA)
- `.gcloudignore` required — prevents uploading node_modules
- Manual trigger: `gcloud builds submit --config=cloudbuild.yaml --project=PROJECT_ID`

### Cloud SQL Access

- Local access via `cloud-sql-proxy` on a unique port per project
- Port convention: 5432 (system Postgres), 5433+ (Docker dev / Cloud SQL proxy)
- Cloud Run connects via Unix socket (`/cloudsql/INSTANCE_CONNECTION_NAME`)

### Infra TODOs

- [ ] Optimize Cloud Build steps — consider combining lint into Docker build
- [ ] Set up Cloud Build triggers (auto-deploy on push to main)
- [ ] Cloud Armor IP allowlisting for production
