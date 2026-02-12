---
name: devax-code-review
description: Comprehensive, project-agnostic code review with 12 categories (8 quality + 4 security) and 3 depth levels. Produces a graded report with actionable findings.
---

Run a structured code review on the current project. Auto-detects framework (Next.js, Prisma, etc.) and produces a graded report.

## Usage

- `/devax-code-review` — Standard review (all 8 quality categories)
- `/devax-code-review quick` — Fast post-session check (4 key categories)
- `/devax-code-review full` — Comprehensive review with security audit (all 12 categories)

## Depth Levels

| Depth | When to run | Categories |
|-------|-------------|-----------|
| `quick` | After every phase / work session | 4: Type Safety, DRY, Component Architecture, Error Handling |
| `standard` | Before deploys | 8: All quality categories |
| `full` | Before launch / quarterly / investor demos | 12: All quality + all security |

## Steps

### 1. Detect Project Context

Read the project's `CLAUDE.md` and `package.json` to identify:
- **Project name** and description
- **Framework** (Next.js, Express, etc.)
- **Language** (TypeScript, JavaScript)
- **ORM** (Prisma, Drizzle, etc.)
- **Source directory** (usually `src/`)
- **Current git commit** hash (short)

If no `CLAUDE.md` exists, infer from `package.json` and directory structure.

### 2. Determine Depth

Parse the argument:
- No argument or `standard` → run categories 1-8
- `quick` → run categories 1, 2, 4, 6
- `full` → run categories 1-12

### 3. Run Automated Checks

For each active category, run the automated checks described below. Use Grep and Glob tools for file analysis. Track findings with severity levels: **Critical**, **High**, **Medium**, **Low**, **Info**.

### 4. Produce Report

Write the report to `claude_docs/CODE-REVIEW.md` using the format specified in the Report Output section below.

Show the executive summary to the user inline, and tell them the full report location.

---

## Categories

### Category 1: Type Safety and Correctness

**Automated checks:**
- Grep for `any` type usage in `src/` (excluding `node_modules`, test files, type declaration files)
- Grep for `as any` casts
- Grep for `@ts-ignore` and `@ts-expect-error`
- Grep for untyped function parameters (functions with `(param)` instead of `(param: Type)`)
- Check `tsconfig.json` for `strict: true`

**Grading:**
- **A** = Zero `any` types, strict mode on, no ts-ignore
- **B** = 1-5 `any` in non-critical paths (utils, tests)
- **C** = `any` in API handlers or business logic
- **D** = Widespread `any` usage or strict mode off

### Category 2: Code Duplication (DRY)

**Automated checks:**
- Count lines in all page files — flag any > 400 lines
- Identify repeated UI patterns (search for common CTA blocks, banner patterns, header patterns)
- Search for duplicate data definitions (same constants defined in multiple files)
- Search for copy-pasted fetch/API patterns
- Search for inline reference data that should be centralized (dollar amounts, country lists)

**Grading:**
- **A** = Minimal duplication, shared components for common patterns
- **B** = 1-2 repeated patterns, mostly DRY
- **C** = 3-5 duplicated patterns across files
- **D** = Pervasive copy-paste, inline data scattered across many files

### Category 3: Data Access Patterns

**Automated checks:**
- Grep for direct ORM/Prisma calls in route handlers (`prisma.` in `api/` routes)
- Check for `$transaction` usage (should exist for multi-step mutations)
- Look for N+1 query patterns (loops containing await prisma calls)
- Check if a repository/DAL layer exists (`repositories/` or `dal/` directory)
- Count total direct ORM call sites

**Grading:**
- **A** = Clean DAL/repository layer, transactions for multi-step ops
- **B** = Consistent patterns with some direct ORM calls
- **C** = Mixed — some routes use DAL, others call ORM directly
- **D** = ORM calls scattered across all route handlers, no transactions

### Category 4: Component Architecture

**Automated checks:**
- Count lines in all component and page files — flag any > 300 lines
- Count `'use client'` directives — flag unnecessary client components
- Check for inline data constants in page files (should be imported)
- Look for components doing data fetching + rendering (should be split)
- Check for `style jsx` tags (should use Tailwind or CSS modules)

**Grading:**
- **A** = Small focused components (< 200 lines), clean server/client split
- **B** = Mostly good, 1-2 oversized components
- **C** = Multiple oversized components, some inline data
- **D** = Monolithic pages, widespread inline data, no extraction

### Category 5: Reference Data Management

**Automated checks:**
- Grep for hardcoded dollar amounts (`\$[0-9]`, `AUD`, `USD`) in page files
- Grep for inline arrays of countries, test scores, or config data in page files
- Check for a centralized data directory (`lib/data/` or similar)
- Check for `lastVerified` or `source` metadata on reference data
- Count how many page files define their own data constants

**Grading:**
- **A** = All data centralized with metadata (lastVerified, source URLs)
- **B** = Mostly centralized, 1-2 files with inline data
- **C** = Partially centralized — some in data modules, some inline
- **D** = Data scattered across many page files, no metadata

### Category 6: Error Handling and Resilience

**Automated checks:**
- Count try/catch blocks in API routes — every route should have one
- Check for React Error Boundaries
- Check client-side fetch calls for error handling (`.catch()` or try/catch)
- Look for empty catch blocks
- Check for loading states in client components that fetch data
- Verify API responses use consistent status codes and error format

**Grading:**
- **A** = Comprehensive with error boundaries, consistent format, loading states
- **B** = Consistent API error handling, some client gaps
- **C** = API routes covered but client error handling spotty
- **D** = Inconsistent error handling, empty catch blocks

### Category 7: Test Coverage

**Automated checks:**
- Search for test files (`*.test.ts`, `*.test.tsx`, `*.spec.ts`, `__tests__/`)
- Check for test runner config (vitest.config.ts, jest.config.ts, playwright.config.ts)
- Check package.json for test scripts (`"test"`, `"test:coverage"`)
- Count test files vs source files ratio
- Check for CI test integration (in cloudbuild.yaml, .github/workflows, etc.)

**Grading:**
- **A** = 80%+ coverage with CI integration
- **B** = 50%+ coverage or comprehensive unit tests
- **C** = Some tests exist, partial coverage
- **D** = Zero test files or no test runner configured

### Category 8: Feature Modularity and Decoupling

**Automated checks:**
- Check for feature flag system (feature registry, env-var toggles, `useFeature` hook)
- Check navigation for hardcoded arrays vs registry consumption
- Look for runtime toggle capability
- Check for tier/access gating patterns
- Check if features can be independently enabled/disabled

**Grading:**
- **A** = Runtime feature toggles with tier-gating and registry
- **B** = Environment variable toggles, some decoupling
- **C** = Features are somewhat modular but tightly coupled to nav
- **D** = Fully hardcoded navigation, no toggle capability

### Category 9: Auth and Access Control (security — `full` only)

**Automated checks:**
- Grep for auth/session checks in all API routes (every mutating route needs auth)
- Check middleware.ts for route protection patterns
- Grep for role checks on admin routes
- Verify CSRF protection (tokens or SameSite cookies)
- Check session config (httpOnly, secure, sameSite flags)

**Severity mapping:**
- Missing auth on mutating route = **Critical**
- Missing role check on admin route = **High**
- Missing CSRF = **Medium**
- Session misconfiguration = **Medium**

### Category 10: Data Protection and Privacy (security — `full` only)

**Automated checks:**
- Grep for PII fields (passport, ssn, dateOfBirth, etc.) in console.log/console.error
- Check signed URL expiry times (should be < 1 hour)
- Verify error responses don't leak PII or stack traces
- Check for encryption patterns on sensitive data
- Verify `.env` and credential files are in `.gitignore`

**Severity mapping:**
- PII in logs = **Critical**
- Unencrypted PII at rest = **High**
- Long-lived signed URLs (> 1 hour) = **Medium**
- PII in error responses = **Medium**

### Category 11: Input Validation and Injection (security — `full` only)

**Automated checks:**
- Grep for `dangerouslySetInnerHTML` — each usage needs justification
- Grep for raw SQL queries (Prisma.$queryRaw without parameterization)
- Check all POST/PATCH/PUT/DELETE routes for Zod or similar validation
- Check file upload handlers for MIME type validation
- Look for user input rendered without sanitization

**Severity mapping:**
- XSS via dangerouslySetInnerHTML with user data = **Critical**
- Unvalidated POST route = **High**
- Missing file upload validation = **Medium**
- Missing input length limits = **Low**

### Category 12: Infrastructure Security (security — `full` only)

**Automated checks:**
- Run `npm audit` and parse output (if available)
- Grep for hardcoded secrets/API keys in source files
- Check for security headers (CSP, X-Frame-Options, etc.)
- Verify `.env*` files are in `.gitignore`
- Check CORS configuration
- Check rate limiting implementation

**Severity mapping:**
- Hardcoded secret in source = **Critical**
- Critical CVE from npm audit = **Critical** (match npm severity)
- Missing CSP = **Medium**
- Missing rate limiting = **Medium**

---

## Report Output Format

Write the report to `claude_docs/CODE-REVIEW.md`:

```markdown
# Code Review Report: [Project Name]

**Date:** YYYY-MM-DD | **Depth:** quick|standard|full | **Commit:** [short hash]

## Executive Summary

**Overall Grade: [A-D]** | Quality: [A-D] | Security: [A-D or N/A]

[2-3 sentence summary of the most important findings and overall health.]

## Scorecard

| # | Category | Grade | Critical | High | Medium | Low |
|---|----------|-------|----------|------|--------|-----|
| 1 | Type Safety | | | | | |
| 2 | Code Duplication (DRY) | | | | | |
| 3 | Data Access Patterns | | | | | |
| 4 | Component Architecture | | | | | |
| 5 | Reference Data | | | | | |
| 6 | Error Handling | | | | | |
| 7 | Test Coverage | | | | | |
| 8 | Feature Modularity | | | | | |
| 9 | Auth & Access Control | | | | | |
| 10 | Data Protection | | | | | |
| 11 | Input Validation | | | | | |
| 12 | Infrastructure Security | | | | | |

## Findings by Category

### Category N: [Name] — Grade [X]

[Explanation of findings, with file:line references]

**Issues:**
- **[Severity]** [Description] — `file/path.ts:42`

## Priority Actions

### Critical
- [ ] [Action item with effort estimate]

### High
- [ ] [Action item with effort estimate]

### Medium
- [ ] [Action item with effort estimate]

### Low
- [ ] [Action item with effort estimate]

## Compliance Checklist

- [ ] OWASP Top 10 (only for `full` depth)
- [ ] Australian Privacy Act APP 11 (if PII handling detected)
- [ ] GDPR considerations (if EU users possible)

## Metrics

| Metric | Value |
|--------|-------|
| Files analyzed | |
| Lines of code | |
| API routes | |
| Components | |
| Test files | |
| Categories reviewed | |
```

---

## Important

- **Never modify source code** — this skill only reads and reports
- **Always write the report** to `claude_docs/CODE-REVIEW.md` (overwriting previous)
- **Show the executive summary** inline after running, with the full report path
- **Grade conservatively** — when in doubt, grade one level lower
- **Be specific** — every finding must include a file path and line number
- **Prioritize actionable** — focus on things that can actually be fixed, not theoretical concerns
- This skill works on any project with a `src/` directory — it's not specific to any framework
