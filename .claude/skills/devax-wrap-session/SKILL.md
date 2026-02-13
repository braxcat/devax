---
name: devax-wrap-session
description: End-of-session cleanup — update claude_docs/, commit all changes, push, update MEMORY.md, and post to Slack. The "I'm done for today" command.
---

End-of-session wrap-up. Updates docs, commits, pushes, updates memory, and posts to Slack.

## Usage
- `/devax-wrap-session` — Run the full end-of-session sequence
- `/devax-wrap-session quick` — Skip Slack posting

## Steps

### 1. Identify the project

Read the project's `CLAUDE.md` to find:
- **Project name** (from the header)
- Confirm `claude_docs/` exists

If `claude_docs/` doesn't exist, ask: "No claude_docs/ found — run /devax-scaffold-docs first?"

### 2. Update documentation

Analyze recent changes and update `claude_docs/`:

**2a. Analyze:** Run `git log` since the last CHANGELOG or WORKLOG entry to understand what changed.

**2b. Draft updates** for each doc that has changes to record:

#### CHANGELOG.md
- Draft a new entry from the git log
- Use `## [Unreleased]` or `## [Session — YYYY-MM-DD]` as heading (not `[Phase N]` — that's for deploys)
- Include Added/Fixed/Changed sections as appropriate

#### ROADMAP.md
- Check if any phases should be marked COMPLETE
- If so, update the Phase Summary table
- Skip if no phases changed

#### FEATURES.md
- Add or update entries if new user-facing features were committed
- Skip if no feature changes

#### WORKLOG.md
- Add a session entry with today's date
- Note what was done, key files modified, decisions made

**2c. Show all drafted changes** to the user for approval before writing any files.

If nothing meaningful was found in the git log, say so and move to step 3.

### 2d. Update user docs (optional)

If `src/content/docs/` exists and feature source files changed (check `git diff --name-only` for files under `src/app/`, `src/components/`, `src/lib/`):

Ask: "Feature code changed — update user docs? (y/n)"
- **y:** Run `/devax-update-user-docs` to detect and update affected MDX docs
- **n:** Skip

If `src/content/docs/` does not exist, skip silently.

### 3. Commit all outstanding changes

Run `git status` and show the user what's uncommitted (both code and doc changes).

If there are uncommitted changes:
- Show the full list of modified/untracked files
- Ask the user to confirm what should be committed
- Stage the approved files
- Draft a commit message summarizing the session's work
- Show the message for approval, then commit

If everything is already committed, say "Nothing to commit" and move on.

### 4. Push to remote

Check if the current branch tracks a remote:
- If yes, run `git push` and report success/failure
- If no remote tracking branch, ask: "No remote tracking branch — push with `-u origin <branch>`?"

If the push fails (e.g. behind remote), report the error and suggest resolution (pull, rebase, etc.). Do NOT force push.

### 5. Update MEMORY.md

Review what was done this session and update the Claude auto-memory file.

The memory file location follows Claude Code's convention:
- `~/.claude/projects/<project-path>/memory/MEMORY.md`

Read the current MEMORY.md (if it exists) and update or add entries for:
- **Gotchas encountered** — things that failed unexpectedly, workarounds found
- **Patterns learned** — new patterns, conventions, or approaches discovered
- **Decisions made** — architectural choices, tool selections, trade-offs
- **Project state** — what phase the project is in, what's deployed, what's next

Show the proposed memory updates to the user before writing.

Keep MEMORY.md concise — it auto-loads into every conversation's context. Link to separate topic files for detailed notes.

### 6. Sync devax skill lists

Check if the devax README.md and CLAUDE.md skill tables match the actual skill files on disk.

**How to check:**
1. List all directories in `.claude/skills/` (each directory = one skill, ignore README.md)
2. Compare against the skill tables in `infra/devax/README.md` and `infra/devax/CLAUDE.md`
3. If any skill is missing from either file, or any listed skill doesn't have a file, flag the drift

**If drift is found:**
- Show the user which skills are missing or stale
- Propose edits to both files
- Apply after user approval
- **README.md is public** — never add Bosun/business skills to it (those are behind BUSINESS markers in CLAUDE.md only)

**If no drift:** Say "Devax skill lists in sync" and move on.

### 7. Post to Slack

If the user said `/wrap-session quick`, skip this step.

Check if `SLACK_BOT_TOKEN` is set:
- If yes, ask: "Post updates to Slack?" If approved, run `/devax-post-update all` with `--context wrap` so Slack messages show wrap-specific headings (e.g. "Session Wrap", "Session Changes")
- If not set, remind the user they can run `/devax-post-update all --context wrap` later

### 8. Summary

Report everything that happened:
- Docs updated (list which ones, or "none needed")
- Commit created (hash + message) or "nothing to commit"
- Push status (success, skipped, or error)
- Memory entries added/updated (list them)
- Slack posts sent or skipped

## Important

- **Every step asks for confirmation** — never auto-commit, auto-push, or auto-write without showing the user first
- **Steps are independent** — if one step fails or is skipped, continue to the next
- **No deploying** — this skill never builds, deploys, or runs tests. Use `/devax-deploy` for that.
- **No force operations** — never `git push --force`, `git reset --hard`, or similar
- **CHANGELOG uses session headings** — `[Unreleased]` or `[Session — date]`, not `[Phase N]`
- Works with any project that has the standard `claude_docs/` structure
