# /devax-code-review

Comprehensive, project-agnostic code review skill for Claude Code. Produces a graded report across 12 categories (8 quality + 4 security) at three depth levels.

## Quick Start

```
/devax-code-review              # Standard — 8 quality categories (~15 min)
/devax-code-review quick        # Fast — 4 key categories (~5 min)
/devax-code-review full         # Full — all 12 categories with security (~30 min)
```

## What It Does

1. **Detects** project framework from `CLAUDE.md` and `package.json`
2. **Analyzes** source code using automated grep/glob checks
3. **Grades** each category A through D with severity-tagged findings
4. **Writes** a structured report to `claude_docs/CODE-REVIEW.md`
5. **Shows** the executive summary inline

## Depth Levels

| Depth | Categories | When to Use |
|-------|-----------|-------------|
| **quick** | Type Safety, DRY, Component Architecture, Error Handling | After a work session or phase completion |
| **standard** | All 8 quality categories | Before deploying to production |
| **full** | All 12 (quality + security) | Before launch, quarterly audits, investor demos |

## Categories

### Quality (1-8)

| # | Category | What It Checks |
|---|----------|----------------|
| 1 | **Type Safety** | `any` types, `@ts-ignore`, strict mode, untyped params |
| 2 | **Code Duplication** | Repeated UI patterns, inline data, copy-pasted boilerplate |
| 3 | **Data Access** | Scattered ORM calls, missing transactions, N+1 queries |
| 4 | **Component Architecture** | Oversized components, unnecessary `use client`, inline data |
| 5 | **Reference Data** | Hardcoded values, data duplication, missing metadata |
| 6 | **Error Handling** | Missing boundaries, inconsistent responses, empty catches |
| 7 | **Test Coverage** | Test files, runner config, CI integration, coverage % |
| 8 | **Feature Modularity** | Feature flags, nav coupling, tier-gating, registry |

### Security (9-12) — `full` depth only

| # | Category | What It Checks |
|---|----------|----------------|
| 9 | **Auth & Access Control** | Route auth guards, role enforcement, CSRF, session config |
| 10 | **Data Protection** | PII in logs, signed URL TTL, encryption, error leaks |
| 11 | **Input Validation** | XSS, SQL injection, Zod coverage, file upload MIME |
| 12 | **Infrastructure Security** | npm audit, hardcoded secrets, CSP, CORS, rate limiting |

## Grading Scale

| Grade | Meaning |
|-------|---------|
| **A** | Excellent — meets or exceeds best practices |
| **B** | Good — minor issues in non-critical areas |
| **C** | Fair — notable gaps that should be addressed |
| **D** | Poor — significant issues requiring priority attention |

## Severity Levels

| Severity | Meaning |
|----------|---------|
| **Critical** | Must fix immediately — security vulnerability or data loss risk |
| **High** | Fix before next deploy — significant quality or security gap |
| **Medium** | Fix soon — noticeable issue that degrades quality |
| **Low** | Fix when convenient — minor improvement |
| **Info** | Observation — no action required |

## Project Compatibility

Works on any project with a `src/` directory. Auto-detects:
- **Next.js** (App Router or Pages Router)
- **Express / Fastify** (Node.js APIs)
- **React** (standalone SPAs)
- **Prisma / Drizzle** (ORM detection)
- **TypeScript / JavaScript**

## Output

The full report is written to `claude_docs/CODE-REVIEW.md`. If `claude_docs/` doesn't exist, the skill creates it.

---

## Mock Report

Below is an example of the report output for a mid-maturity Next.js application:

---

# Code Review Report: My Project

**Date:** 2026-02-12 | **Depth:** full | **Commit:** f050c75

## Executive Summary

**Overall Grade: B-** | Quality: B- | Security: B+

Strong type safety foundation (zero `any` types, strict mode) and solid error handling across all API routes. Main weaknesses are scattered reference data, significant code duplication in tool pages, and zero test coverage. Security posture is good with proper auth guards and secrets management, though signed URL TTL should be tightened.

## Scorecard

| # | Category | Grade | Critical | High | Medium | Low |
|---|----------|-------|----------|------|--------|-----|
| 1 | Type Safety | **A+** | 0 | 0 | 0 | 0 |
| 2 | Code Duplication (DRY) | **C-** | 0 | 2 | 3 | 1 |
| 3 | Data Access Patterns | **C** | 0 | 1 | 2 | 0 |
| 4 | Component Architecture | **C+** | 0 | 1 | 3 | 2 |
| 5 | Reference Data | **C-** | 0 | 2 | 2 | 1 |
| 6 | Error Handling | **A-** | 0 | 0 | 1 | 1 |
| 7 | Test Coverage | **D** | 0 | 1 | 0 | 0 |
| 8 | Feature Modularity | **D** | 0 | 1 | 1 | 0 |
| 9 | Auth & Access Control | **A** | 0 | 0 | 0 | 1 |
| 10 | Data Protection | **B+** | 0 | 0 | 1 | 1 |
| 11 | Input Validation | **A-** | 0 | 0 | 1 | 0 |
| 12 | Infrastructure Security | **B** | 0 | 0 | 2 | 1 |

## Findings by Category

### Category 1: Type Safety — Grade A+

Zero `any` types across the entire `src/` directory. TypeScript strict mode is enabled. No `@ts-ignore` or `@ts-expect-error` directives found. All function parameters are typed. Zod schemas enforce runtime validation on all API boundaries.

**Issues:** None

---

### Category 2: Code Duplication (DRY) — Grade C-

The "Ask Wally" CTA block is copy-pasted across 14 page files (~60 lines each, ~840 lines total). Page headers follow a near-identical pattern in 21 files. Info banners repeat across 8 files with minor text variations.

**Issues:**
- **High** Ask Wally CTA duplicated in 14 files — should be `<AskWallyCTA>` component — `src/app/(protected)/tools/doc-check/page.tsx:351`
- **High** Page header pattern (h1 + description) repeated in 21 tool/guide/service pages — `src/app/(protected)/tools/eligibility/page.tsx:207`
- **Medium** Info banner pattern duplicated across 8 files with identical styling — `src/app/(protected)/tools/police-clearance/page.tsx:45`
- **Medium** Eligibility check logic partially duplicates country data from `lib/countries/` — `src/app/(protected)/tools/eligibility/page.tsx:38`
- **Medium** English score equivalence table defined in 2 separate files — `src/app/(protected)/tools/english-check/page.tsx:23` and `src/app/(protected)/tools/english-prep/page.tsx:47`
- **Low** Visa result card pattern repeated 3x in eligibility results — `src/app/(protected)/tools/eligibility/page.tsx:361`

---

### Category 3: Data Access Patterns — Grade C

Prisma client is called directly in 41 API route handlers. No repository layer exists. Document upload flow (OCR -> update -> auto-populate -> auto-checklist) is not wrapped in a transaction, risking partial state on failure.

**Issues:**
- **High** Document upload pipeline not in `$transaction` — partial OCR failure leaves inconsistent state — `src/app/api/documents/route.ts:45`
- **Medium** Direct `prisma.user.findUnique()` in 12 routes instead of shared `getUserProfile()` — `src/app/api/user/profile/route.ts:15`
- **Medium** No N+1 prevention — journey progress fetches include dependants in a loop — `src/app/api/journey/progress/route.ts:28`

---

### Category 4: Component Architecture — Grade C+

21 tool/guide/service pages average 386 lines each. The eligibility checker is 480 lines with inline eligibility logic, country data, and result rendering in a single file. Several pages use `'use client'` primarily for a single `useState` that could be refactored.

**Issues:**
- **High** Eligibility page is 480 lines — should extract eligibility logic, country data, and result cards — `src/app/(protected)/tools/eligibility/page.tsx`
- **Medium** 3 pages use `style jsx` instead of Tailwind utilities — `src/app/(protected)/tools/eligibility/page.tsx:463`
- **Medium** English check page (417 lines) mixes score validation, equivalence lookup, and rendering — `src/app/(protected)/tools/english-check/page.tsx`
- **Medium** Destination compare page has 60+ lines of inline country comparison data — `src/app/(protected)/tools/destination-compare/page.tsx`
- **Low** Compliance page could extract work-hours tracker widget — `src/app/(protected)/tools/compliance/page.tsx`
- **Low** 5 pages use `min-h-screen bg-gradient-to-b` wrapper instead of standard `space-y-6` — layout inconsistency

---

### Category 5: Reference Data — Grade C-

Visa fees are centralized in `budget-reference.ts` (good) but also hardcoded in `eligibility/page.tsx` ($670, $670, $2000, $2300). English test scores defined in 2 separate files. Processing times scattered across pages. Fee conflict found: eligibility page uses $650 for WHV in one place while budget-reference has $670.

**Issues:**
- **High** Visa fees hardcoded in eligibility page instead of importing from budget-reference — `src/app/(protected)/tools/eligibility/page.tsx:113`
- **High** English score data duplicated in english-check and english-prep pages — `src/app/(protected)/tools/english-check/page.tsx:23`
- **Medium** Processing times (1-48 hours, 4-6 weeks) hardcoded inline with no source metadata — `src/app/(protected)/tools/eligibility/page.tsx:114`
- **Medium** FAFSA eligible schools and loan rates inline (12 schools, 3 loan types) — `src/app/(protected)/services/fafsa/page.tsx:23`
- **Low** DASP tax rates inline instead of centralized — `src/app/(protected)/guides/super/page.tsx:16`

---

### Category 6: Error Handling — Grade A-

All 51 API routes have try/catch blocks with consistent error response format. Client-side fetches mostly handle errors. No empty catch blocks found.

**Issues:**
- **Medium** No React Error Boundary — unhandled component errors show blank screen — `src/app/(protected)/layout.tsx`
- **Low** 2 client fetch calls use `.catch(console.error)` without user feedback — `src/app/(protected)/tools/doc-check/page.tsx:103`

---

### Category 7: Test Coverage — Grade D

Zero test files in the repository. No test runner configured. No test scripts in package.json. A test strategy document exists at `claude_docs/TESTING.md` but has not been implemented.

**Issues:**
- **High** Zero test files — no regression protection for 51 API routes and 39 components — project-wide

---

### Category 8: Feature Modularity — Grade D

Navigation sidebar has hardcoded arrays for all nav items. No feature flag system exists. Features cannot be independently toggled on/off. No tier-gating mechanism for paid features.

**Issues:**
- **High** Sidebar navigation fully hardcoded — cannot toggle features without code changes — `src/components/layout/Sidebar.tsx:24`
- **Medium** No feature flag system for A/B testing or tier-gating — project-wide

---

### Category 9: Auth & Access Control — Grade A

All protected API routes check session via `getServerSession()`. Admin routes verify `role === 'admin'`. Middleware guards `/admin/*` routes. NextAuth config uses httpOnly secure cookies.

**Issues:**
- **Low** No explicit CSRF token — relies on SameSite cookie + Next.js built-in protection — `src/lib/auth.config.ts`

---

### Category 10: Data Protection — Grade B+

Sensitive document data (passports, bank statements) stored in GCS with signed URLs. PII fields (passport number, DOB) are not logged. Error responses use generic messages.

**Issues:**
- **Medium** Signed URL TTL is 60 minutes — consider reducing to 15 minutes for passport documents — `src/lib/gcs.ts:42`
- **Low** Conversation logs may contain PII shared by user in chat — no automated redaction — `src/app/api/chat/route.ts`

---

### Category 11: Input Validation — Grade A-

Zod validation on all POST/PATCH/PUT routes. No `dangerouslySetInnerHTML` usage found. Prisma handles parameterized queries. File upload validates MIME type.

**Issues:**
- **Medium** Chat message input has no length limit at the Zod level (relies on LLM token limit) — `src/lib/validation.ts:85`

---

### Category 12: Infrastructure Security — Grade B

Secrets managed via GCP Secret Manager. `.env*` files properly gitignored. Rate limiting implemented on chat and auth endpoints.

**Issues:**
- **Medium** `npm audit` reports 2 moderate vulnerabilities in transitive dependencies — run `npm audit fix`
- **Medium** No Content-Security-Policy header configured — `next.config.js`
- **Low** Cloud SQL authorized network includes a specific IP — review periodically — `cloudbuild.yaml`

---

## Priority Actions

### Critical
_(none)_

### High
- [ ] **Extract Ask Wally CTA** to shared `<AskWallyCTA>` component — eliminates ~840 lines (2 hours)
- [ ] **Centralize reference data** — move visa fees, English scores, processing times to `src/lib/data/` (4 hours)
- [ ] **Add test infrastructure** — install Vitest, write first tests for Zod schemas and data modules (3 hours)
- [ ] **Create feature flag system** — registry + sidebar integration + tier-gating (6 hours)
- [ ] **Wrap document upload in `$transaction`** — prevent partial state on OCR failure (1 hour)

### Medium
- [ ] Add React Error Boundary in protected layout (30 min)
- [ ] Reduce signed URL TTL to 15 minutes for sensitive documents (15 min)
- [ ] Add Content-Security-Policy header (1 hour)
- [ ] Add chat message length limit to Zod schema (15 min)
- [ ] Fix `style jsx` usage — convert to Tailwind animations (30 min)
- [ ] Run `npm audit fix` for moderate vulnerabilities (15 min)

### Low
- [ ] Extract DASP tax rates to centralized data module
- [ ] Standardize page wrapper classes (remove `min-h-screen bg-gradient-to-b` pattern)
- [ ] Add automated PII redaction for conversation logs

## Compliance Checklist

- [x] **OWASP Top 10** — No critical injection, auth, or data exposure issues found
- [x] **Australian Privacy Act APP 11** — PII handled appropriately, not logged, encrypted at rest
- [ ] **GDPR** — Not assessed (no EU users currently, but consider if expanding)

## Metrics

| Metric | Value |
|--------|-------|
| Files analyzed | 142 |
| Lines of code | 48,576 |
| API routes | 51 |
| Components | 39 |
| Test files | 0 |
| Categories reviewed | 12 |
| Time elapsed | ~28 min |
