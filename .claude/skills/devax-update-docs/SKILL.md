---
name: devax-update-docs
description: Update claude_docs/ after a work session (CHANGELOG, ROADMAP, FEATURES, WORKLOG), optionally commit and post to Slack. Use when work was done but not deployed.
---

Update project documentation after a work session — without deploying.

## Usage
- `/devax-update-docs` — Update all docs based on recent commits
- `/devax-update-docs changelog` — Update only CHANGELOG
- `/devax-update-docs worklog` — Update only WORKLOG
- `/devax-update-docs dry-run` — Show what would be updated without writing

## Steps

### 1. Identify the project

Read the project's `CLAUDE.md` to find:
- **Project name** (from the header)
- **Documentation Index** (to confirm `claude_docs/` paths exist)

If `claude_docs/` doesn't exist, suggest running `/devax-scaffold-docs` first.

### 2. Analyze recent changes

Run `git log` to understand what was done since the last documentation update:
- Check the date of the most recent entry in `claude_docs/CHANGELOG.md`
- Check the date of the most recent entry in `claude_docs/WORKLOG.md`
- Get all commits since the earlier of those two dates
- Summarize the changes (features added, bugs fixed, refactors, etc.)

If `/update-docs dry-run`, show the summary and stop here.

### 3. Update documentation

Update only the docs that have changes to record. Skip any doc where nothing changed.

If the user specified a specific doc (e.g. `/update-docs changelog`), only update that one.

#### CHANGELOG.md
- Draft a new entry in Keep a Changelog format
- Use `## [Unreleased]` or `## [Session — YYYY-MM-DD]` as the heading (not `[Phase N]` — that's for deploys)
- Include Added/Fixed/Changed sections as appropriate
- Show the draft to the user for approval before writing

#### ROADMAP.md
- Check if any phases should be marked COMPLETE based on recent work
- If so, update the Phase Summary table (set status to COMPLETE and date to today)
- Show changes to user for approval
- If no phases changed, skip this doc

#### FEATURES.md
- If new user-facing features were committed, add or update entries
- Only modify if there are actual feature changes to document
- Show changes to user for approval

#### WORKLOG.md
- Add a session entry with today's date
- Note what was done, files created/modified, and any key decisions
- Show the draft to the user for approval before writing

### 4. Commit doc changes

After the user approves the doc updates:
- Stage only the modified `claude_docs/` files
- Show the staged changes and ask the user if they want to commit
- If yes, commit with message: `Update docs: CHANGELOG, WORKLOG` (listing which docs were updated)
- Do NOT push — let the user decide when to push

### 5. Post to Slack (optional)

After docs are committed, check if `SLACK_BOT_TOKEN` is set.

If set, ask the user: "Post updates to Slack?"
- If yes, run `/devax-post-update all` with `--context session` so Slack messages show session-specific headings (e.g. "Session Update", "Development Progress")
- If no, skip

If not set, remind the user they can run `/devax-post-update all --context session` later.

### 6. Summary

Report:
- Docs updated (list which ones)
- Commit created (hash) or skipped
- Slack posts sent or skipped

## Important

- Always show doc changes to the user before writing — never auto-write doc updates
- This skill does NOT deploy, build, or run tests — it only updates documentation
- CHANGELOG entries use `[Unreleased]` or `[Session]` headings, not `[Phase N]` — phase headings are reserved for `/devax-deploy`
- If no meaningful changes are found in the git log, say so and stop — don't create empty entries
- This skill works with any project that has the standard `claude_docs/` structure
