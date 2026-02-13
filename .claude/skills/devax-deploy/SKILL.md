---
name: devax-deploy
description: Deploy the current project to GCP Cloud Run and update all documentation (CHANGELOG, ROADMAP, FEATURES, WORKLOG). Automates the full Post-Deploy Checklist.
---

Automate the full deploy + doc update workflow for GCP projects.

## Usage
- `/devax-deploy` — Deploy and update all docs
- `/devax-deploy dry-run` — Show what would happen without deploying

## Steps

### 1. Identify the project

Read the project's `CLAUDE.md` to find:
- **GCP Project ID** (from the Deployment section)
- **Deploy command** (usually `gcloud builds submit --config=cloudbuild.yaml --project=PROJECT_ID`)
- **Project name** (from the header)

If CLAUDE.md doesn't have a Deployment section, ask the user for the GCP project ID.

### 2. Pre-deploy checks

Run tests and build to verify everything passes before deploying. If either fails, stop and fix the issue.

```bash
npm test           # Skip with --skip-tests flag
npm run build
```

If the user passed `--skip-tests`, skip `npm test` but still run the build.

### 3. Deploy

If the user said `/devax-deploy dry-run`, skip this step and just show what would be deployed (git log since last deploy).

#### 3a. Check for in-flight builds

Before submitting, check if there's already a build running:

```bash
gcloud builds list --project=PROJECT_ID --filter="status=WORKING" --limit=5
```

If a build is already WORKING:
- Show the user the in-flight build ID, start time, and duration so far
- Ask: "A build is already running (BUILD_ID, started X minutes ago). Submit another, or wait for it?"
- If the user says wait, skip to Step 3c (poll the existing build)
- If the user says submit, proceed to Step 3b

#### 3b. Submit the build

Submit the build using `--async` to avoid blocking:

```bash
gcloud builds submit --config=cloudbuild.yaml --project=PROJECT_ID --async
```

This returns immediately with a build ID. Capture the build ID from the output.

#### 3c. Poll for completion

Cloud Build typically takes 6-10 minutes. Poll periodically instead of streaming logs:

```bash
gcloud builds describe BUILD_ID --project=PROJECT_ID --format="value(status)"
```

**Polling strategy:**
- Wait **8 minutes** before the first check (builds typically take 6-10 minutes — don't waste tokens polling early)
- If still WORKING, poll every **60 seconds** after that
- Between polls, do NOT make any tool calls — just wait silently
- After 15 minutes total (timeout), report the build URL and suggest checking manually

When the build finishes:
- **SUCCESS:** Continue to Step 4
- **FAILURE:** Show the build logs tail and stop:
  ```bash
  gcloud builds log BUILD_ID --project=PROJECT_ID | tail -30
  ```

### 4. Update documentation

After a successful deploy, update these docs in `claude_docs/`:

#### CHANGELOG.md
- Read the current changelog
- Get the git log since the last entry (look at the date of the most recent changelog entry)
- Draft a new entry in Keep a Changelog format with Added/Fixed/Changed sections as appropriate
- Show the draft to the user for approval before writing

#### ROADMAP.md
- Check if any phases should be marked COMPLETE
- If so, update the Phase Summary table (set status to COMPLETE and date to today)
- Show changes to user for approval

#### FEATURES.md
- If new features shipped, add or update entries
- Only modify if there are actual feature changes to document

#### WORKLOG.md
- Add a deploy session entry with today's date
- Note what was deployed and which docs were updated

### 4b. Update user docs (optional)

Check if `src/content/docs/` exists in the project.

If yes, ask: "Update user documentation? (y/n/skip)"
- **y:** Run `/devax-update-user-docs` to detect and update affected docs
- **n/skip:** Continue to step 5

If `src/content/docs/` does not exist, skip silently.

Only offer this step after a successful build/deploy.

### 5. Post to Slack

After docs are updated, run `/devax-post-update all` to push updates to Slack channels.

Use `--context deploy` so Slack messages show deploy-specific headings (e.g. "Shipped!", "Changelog").

If `SLACK_BOT_TOKEN` is not set, skip this step and remind the user to run `/devax-post-update all` manually.

### 6. Summary

Report:
- Deploy status (success/failure/dry-run)
- Build duration
- Docs updated (list which ones)
- Slack posts sent (or skipped)

## Important

- Always run `npm run build` before deploying — catch errors before they hit Cloud Build
- Always show doc changes to the user before writing — never auto-commit doc changes
- If any step fails, stop and report the error — don't continue with partial updates
- The deploy command comes from the project's CLAUDE.md, not hardcoded here
- This skill works with any project that has a `cloudbuild.yaml` and the standard `claude_docs/` structure
- **Never use blocking `gcloud builds submit` without `--async`** — builds take 6-10 minutes and burn tokens while waiting
- **Always check for in-flight builds first** — duplicate deploys of the same code waste build minutes
- **Use `gcloud builds describe` for polling**, not `gcloud builds log` (which streams and blocks)
