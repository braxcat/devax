# Devax — Testing

> Test strategy for Devax utilities and validation procedures.
>
> **Status:** Planned. Testing framework to be developed.

---

## Testing Strategy

Devax doesn't have traditional code tests, but validation is important for:
- Skills functionality
- Scripts correctness
- Documentation accuracy
- Portfolio structure integrity

---

## Validation Procedures

### Skills Testing
Manual testing required when skills are updated:

| Skill | Test Procedure |
|-------|---------------|
| `/devax-scaffold-docs` | Run in a test project, verify all 8 docs created correctly |
| `/devax-deploy` | Test with dry-run mode in a target project |
| `/devax-update-docs` | Test doc updates without committing |
| `/devax-wrap-session` | Test full workflow in a safe branch |
| `/devax-post-update` | Test Slack posting (when configured) |

### Script Testing

| Script | Test Procedure |
|--------|---------------|
| `add-repo.sh` | Test adding a repo to personal/ or expl/ |
| `gate` | Test list, add, remove commands |
| `dev-updates/` | Test with mock Slack config |

---

## Project-Level Testing

Each portfolio project maintains its own testing. Refer to each project's `CLAUDE.md` for testing documentation.

## Priority Modules for Future Testing

1. **Workspace structure validator** — Script to check:
   - All portfolio directories exist
   - .gitignore properly configured
   - No secrets committed
   - CLAUDE.md and README.md are in sync

2. **Skills regression tests** — Automated tests for:
   - scaffold-docs creates all required files
   - Documentation index updates correctly
   - File conflict handling works

3. **Cross-project consistency checker** — Validate:
   - All projects have required documentation
   - Git configurations are correct
   - No credential leakage

## Known Gaps

- [ ] No automated testing for Devax utilities yet
- [ ] Skills testing is currently manual
- [ ] No CI/CD for Devax itself
- [ ] Documentation consistency not automatically validated
