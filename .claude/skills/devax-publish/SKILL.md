---
name: devax-publish
description: Publish a sanitized version of devax to the public GitHub repo. Scrubs private info, resets personal history, and pushes.
---

Publish a sanitized version of devax to the public repo.

## Usage
- `/devax-publish` — Preview and publish
- `/devax-publish dry-run` — Preview only (no push)

## How it works

The publish script reads `.devax-publish.json` for scrub rules, copies all tracked files to a temp directory, applies find/replace sanitization, resets personal history files (WORKLOG, CHANGELOG) to clean templates, validates no private terms remain, and pushes to the configured remote.

## Steps

1. **Preview first** — Run the script in dry-run mode:
   ```bash
   cd infra/devax && ./scripts/publish.sh --dry-run
   ```

2. **Show the diff** to the user. Highlight:
   - Which files were scrubbed and what changed
   - Which files were reset to templates
   - Whether validation passed (no private terms remaining)

3. **If `$ARGUMENTS` contains "dry-run"**, stop here. Do not push.

4. **Ask for approval** — "Ready to push sanitized version to the public repo?"

5. **If approved**, run the live publish:
   ```bash
   cd infra/devax && ./scripts/publish.sh
   ```

6. **Report** success or failure. If validation fails, show which terms leaked and where.

## Config

The script reads from `.devax-publish.json` (gitignored):
- `scrub_rules` — Ordered find/replace pairs applied to all tracked files
- `reset_to_templates` — Files replaced with clean template stubs
- `remote` / `branch` — Where to push

## Troubleshooting

- **Validation failure:** A scrub rule's "find" term still appears after replacement. Usually means the term appears in a context not covered by existing rules. Add a new, more specific rule to `.devax-publish.json`.
- **Config not found:** Create `.devax-publish.json` in the devax repo root. See the plan or existing config for format.
