---
name: bosun-wrap-session
description: End-of-session cleanup for business work — update business claude_docs/, optionally push to Confluence, commit, and update memory.
---

End-of-session wrap-up for business operations. Updates business docs, optionally syncs to Confluence, commits, and updates memory.

## Usage
- `/bosun-wrap-session` — Run the full end-of-session sequence
- `/bosun-wrap-session quick` — Skip Confluence sync and Slack

## Steps

### 1. Identify the workspace

Confirm we're in the planning repo root and `docs/business/` exists.

If `docs/business/` doesn't exist, ask: "No business workspace found — run `/bosun-scaffold` first?"

### 2. Update business documentation

Analyze what business work was done this session and update `docs/business/claude_docs/`:

**2a. Analyze:** Review conversation context for business activities — meetings, decisions, pipeline changes, strategy updates, financial changes.

**2b. Draft updates** for each doc that has changes to record:

#### ACTIVITY-LOG.md
- Add entries for meetings, calls, outreach, or milestones from this session

#### STRATEGY.md
- Update if strategy discussions or pivots happened

#### PIPELINE.md
- Update deal stages, new leads, or partnership progress

#### DECISIONS.md
- Log any business decisions made with rationale

#### FINANCES.md
- Update if financial changes were discussed (runway, revenue, costs)

#### METRICS.md
- Update if new metrics were reported or KPIs changed

#### TEAM.md
- Update if team changes were discussed

**2c. Show all drafted changes** to the user for approval before writing any files.

If nothing meaningful happened, say so and move to step 3.

### 3. Confluence sync (optional)

If not running in `quick` mode:
- Ask: "Push business doc changes to Confluence?"
- If yes, run `/bosun-confluence-push` flow

### 4. Commit changes

Run `git status` in the planning repo and show uncommitted business-related changes.

If there are changes:
- Show the list of modified/untracked files in `docs/business/`
- Ask user to confirm what should be committed
- Draft a commit message
- Show for approval, then commit

### 5. Update MEMORY.md

Review what was done and update the Claude auto-memory file with:
- Business decisions made
- Pipeline or strategy changes
- Key contacts or relationships noted
- Gotchas or patterns learned

Show proposed changes before writing.

### 6. Post to Slack

If the user said `/bosun-wrap-session quick`, skip this step.

Check if `SLACK_BOT_TOKEN` is set:
- If yes, ask: "Post business updates to Slack?" If approved, run `/bosun-post-update all` with `--context wrap` so Slack messages show wrap-specific headings
- If not set, remind the user they can run `/bosun-post-update all --context wrap` later

### 7. Summary

Report:
- Business docs updated (list which ones, or "none needed")
- Confluence sync status (pushed, skipped, or not configured)
- Commit created (hash + message) or "nothing to commit"
- Memory entries added/updated
- Slack posts sent or skipped

## Important

- **Every step asks for confirmation** — never auto-write, auto-commit, or auto-push
- **Steps are independent** — if one fails or is skipped, continue to the next
- **Business workspace only** — this skill updates `docs/business/`, not project-level `claude_docs/`
- **No force operations** — never force push or force overwrite
- Uses `/bosun-confluence-push` for Confluence sync (not direct MCP calls)
