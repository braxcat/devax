---
name: devax-update-user-docs
description: Update user documentation (MDX) based on code changes. Detects changed features, updates affected doc pages, or refreshes all docs. Convention-based — works with any project that has src/content/docs/.
---

Update user-facing MDX documentation based on recent code changes.

## Usage
- `/devax-update-user-docs` — Detect changed features, update affected docs
- `/devax-update-user-docs dry-run` — Preview what would be updated without writing
- `/devax-update-user-docs all` — Re-generate all docs (full refresh)
- `/devax-update-user-docs <slug>` — Update a specific doc (e.g. `features/documents`)

## Prerequisites

The project must have:
- `src/content/docs/` directory with MDX files
- `src/content/docs/_config.ts` with category definitions and doc listing helpers
- Each `.mdx` file must have frontmatter with `relatedFeature` field (optional but enables auto-detection)
- A feature registry at `src/lib/features/feature-registry.ts` (optional but enables richer context)

## Steps

### 1. Discover documentation structure

Read `src/content/docs/_config.ts` to understand:
- Available categories and their IDs
- How docs are organized

List all `.mdx` files in `src/content/docs/` with their frontmatter (title, category, relatedFeature, lastUpdated).

If the project doesn't have `src/content/docs/`, stop and tell the user this skill requires the MDX docs infrastructure.

### 2. Determine which docs need updating

**If argument is a specific slug** (e.g. `features/documents`):
- Target only that doc

**If argument is `all`:**
- Target every `.mdx` file

**If no argument (auto-detect):**
- Run `git diff --name-only HEAD~5` to get recently changed files
- Map changed source files to feature IDs using this resolution order:
  1. `src/app/(protected)/<route>/page.tsx` → feature with matching route
  2. `src/components/<name>/` → feature referenced in page imports
  3. `src/lib/<domain>/` → feature that uses that domain
  4. `src/lib/features/` → potentially all features (ask user which to update)
- Find docs with `relatedFeature` matching the affected feature IDs
- If no docs match, report "no docs affected by recent changes" and stop

If `dry-run`, show the list of affected docs and stop here.

### 3. Gather context for each affected doc

For each doc to update, collect:
- **Current MDX content** — the existing `.mdx` file
- **Feature registry entry** — from `feature-registry.ts` (id, name, route, tier, wallyKnowledge)
- **Primary page source** — the page.tsx for the feature's route (cap at 3 source files per doc)
- **Recent git diff** — changes to files related to this feature

### 4. Dispatch subagents for updates

Launch parallel Sonnet subagents (up to 5 at a time), one per affected doc.

Each subagent receives:
- The current MDX content
- Feature info (name, route, tier, wallyKnowledge)
- Source code snippets (page.tsx + key components)
- Recent git diff for related files
- These writing instructions:

> **Writing Guidelines:**
> - Write from the USER's perspective (not developer perspective)
> - Use available MDX components: `<Callout>`, `<FeatureLink>`, `<StepList>`, `<Step>`
> - Keep language simple — many readers are international students with English as a second language
> - Use short sentences and clear headings
> - Include practical "how to" steps, not just feature descriptions
> - Update the `lastUpdated` date in frontmatter to today's date
> - Preserve the existing frontmatter structure (title, description, category, order, relatedFeature, requiredRole)
> - If a feature changed significantly, update the description in frontmatter too
> - Do NOT add emojis unless they were already in the doc

Each subagent writes its updated MDX file directly.

### 5. Review changes

After all subagents complete:
- Show a summary of what changed in each doc (added/removed/modified sections)
- Show a unified diff preview for each modified file
- Ask the user: "Apply these changes? (y/n/edit)"
  - **y**: Changes are already written by subagents — confirm success
  - **n**: Revert each file using `git checkout -- <file>`
  - **edit**: Let the user specify which docs to keep/revert

### 6. Report results

Show:
- Number of docs updated
- List of updated doc slugs with their titles
- Any docs that were skipped (and why)
- Remind user to commit: `git add src/content/docs/ && git commit -m "Update user docs"`

## Source-to-Doc Mapping Reference

How source file paths map to feature IDs:

| Source Path Pattern | Feature Resolution |
|---|---|
| `src/app/(protected)/dashboard/` | `dashboard` |
| `src/app/(protected)/journey/` | `journey` |
| `src/app/(protected)/documents/` | `documents` |
| `src/app/(protected)/statements/` | `statements` |
| `src/app/(protected)/dependants/` | `dependants` |
| `src/app/(protected)/budget/` | `budget` |
| `src/app/(protected)/profile/` | `profile` |
| `src/app/(protected)/chat/` | `chat` |
| `src/app/(protected)/admin/<name>/` | `admin-<name>` |
| `src/app/dev/` | dev-tools docs |
| `src/lib/documents/` | `documents` |
| `src/lib/ocr/` | `documents` |
| `src/lib/workflows/` | `journey` |
| `src/lib/llm/` | `chat` |
| `src/lib/rag/` | `admin-knowledge-base`, `chat` |
| `src/components/chat/` | `chat` |

## Important

- Always show changes to the user before confirming — never silently overwrite docs
- This skill does NOT commit or push — it only updates MDX files
- Subagents should write content appropriate for end users, not developers
- If the feature registry doesn't exist, the skill can still work with manually specified slugs
- This skill is convention-based: any project with `src/content/docs/` can use it
