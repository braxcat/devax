---
name: devax-test-create
description: Generate comprehensive tests for existing code. Accepts file paths, directories, or tier levels (tier1=critical, tier2=integration, tier3=e2e scaffold). Analyzes code and creates colocated test files.
---

Generate comprehensive tests for existing code. Analyzes source files and creates test files with appropriate patterns for utilities, Zod schemas, React components, and API routes.

## Usage

- `/devax-test-create src/lib/encryption.ts` — test a specific file
- `/devax-test-create src/lib/validators/` — test all files in directory
- `/devax-test-create tier1` — test all Tier 1 critical path files
- `/devax-test-create tier2` — test Tier 2 integration files
- `/devax-test-create tier3` — scaffold E2E test infrastructure

## Steps

### 1. Parse Arguments

**File path mode:**
- Test the specified file only
- Verify file exists

**Directory mode:**
- Find all `.ts` and `.tsx` files in directory
- Exclude `index.ts`, barrel files, and files already having tests
- Process each file

**Tier mode:**
- Parse tier argument (`tier1`, `tier2`, `tier3`)
- Apply tier classification logic (see step 3)
- Process all files in that tier

### 2. Check Prerequisites

Before generating any tests, verify test runner is configured:

**Check for test runner config:**
- `vitest.config.ts` (preferred)
- `jest.config.ts`
- `playwright.config.ts` (for E2E)

**If no config found:**
- Tell user: "No test runner configured. Run `/devax-test-scaffold` first to set up Vitest and test infrastructure."
- Exit without generating tests

**Verify test script in package.json:**
- Check for `"test"` script
- Check for `"test:watch"` and `"test:coverage"` (optional but recommended)

### 3. Tier Classification

Read `CLAUDE.md` and `package.json` to understand project context, then classify files into tiers:

#### Tier 1 — Critical Paths (unit tests required)

Files containing:
- Encryption/crypto modules (`encrypt`, `decrypt`, `hash`, `crypto`)
- Validation schemas (Zod, Yup, etc.)
- Authentication logic (`auth`, `session`, `token`)
- Data transformation/builder functions (`transform`, `map`, `build`)
- Currency/money conversion (`exchange`, `currency`, `rate`)
- Sensitive data handling (files with `ssn`, `passport`, `pii` in context)
- API routes with mutations (POST, PUT, PATCH, DELETE handlers)

**Priority:** All Tier 1 files must have comprehensive tests

#### Tier 2 — Integration (component + flow tests)

Files containing:
- React components (`.tsx` files in `components/`)
- Form components (validation + submission flows)
- Dashboard and page components
- Complex hooks (`useEffect` with multiple dependencies)
- Multi-step workflows

**Priority:** Test rendering, user interaction, and data flows

#### Tier 3 — E2E (scaffold only)

For `tier3` mode, DO NOT generate individual tests. Instead:

1. Check if Playwright is configured
2. If not, create `playwright.config.ts` with base config
3. Create `tests/e2e/` directory structure
4. Create helper utilities in `tests/e2e/helpers/`
5. Create ONE example E2E test showing the pattern
6. Tell user: "E2E scaffold complete. Write specific E2E tests as needed for critical user journeys."

### 4. Test Generation Patterns

For each file, determine its type and apply the appropriate pattern:

#### Pattern A: Utility/Service Files

**Target:** Pure functions, helpers, builders, transformers

**Test structure:**
```typescript
import { describe, it, expect, vi } from 'vitest'
import { functionName } from '../module-name'

describe('moduleName', () => {
  describe('functionName', () => {
    it('should handle happy path', () => {
      // Test with valid input
    })

    it('should handle edge cases', () => {
      // Test with empty input, boundary values
    })

    it('should handle errors', () => {
      // Test error paths
    })
  })
})
```

**Coverage requirements:**
- Happy path (valid input → expected output)
- Edge cases (empty, null, undefined, boundary values)
- Error paths (invalid input → throws or returns error)

**Mocking rules:**
- Mock external dependencies (Prisma, fetch, APIs)
- NEVER make real network calls
- Use `vi.fn()` for function mocks
- Use `vi.mock()` for module mocks

#### Pattern B: Zod Validation Schemas

**Target:** Files exporting Zod schemas (`.parse()`, `.safeParse()`)

**Test structure:**
```typescript
import { describe, it, expect } from 'vitest'
import { schemaName } from '../schema-file'

describe('schemaName', () => {
  it('should accept valid data', () => {
    const validData = { /* all required fields */ }
    expect(() => schemaName.parse(validData)).not.toThrow()
  })

  describe('required fields', () => {
    it('should reject missing fieldName', () => {
      const data = { /* missing one field */ }
      expect(() => schemaName.parse(data)).toThrow()
    })
    // Repeat for each required field
  })

  describe('constraints', () => {
    it('should reject fieldName below minimum', () => {
      // Test min constraint
    })

    it('should reject fieldName above maximum', () => {
      // Test max constraint
    })

    it('should reject invalid enum value', () => {
      // Test enum constraint
    })
  })

  describe('type coercion', () => {
    it('should coerce string to number', () => {
      // Test if schema uses .coerce()
    })
  })
})
```

**Coverage requirements:**
- Valid data acceptance (one test with all fields valid)
- Each required field (test missing → failure)
- Each constraint (min, max, length, format, enum, regex)
- Type coercion if applicable

#### Pattern C: React Components

**Target:** `.tsx` files exporting React components

**Test structure:**
```typescript
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ComponentName from '../ComponentName'

describe('ComponentName', () => {
  it('should render with required props', () => {
    render(<ComponentName prop="value" />)
    expect(screen.getByText('Expected Text')).toBeInTheDocument()
  })

  it('should handle user interaction', async () => {
    const user = userEvent.setup()
    const mockHandler = vi.fn()
    render(<ComponentName onClick={mockHandler} />)

    await user.click(screen.getByRole('button'))
    expect(mockHandler).toHaveBeenCalledTimes(1)
  })

  it('should conditionally display content', () => {
    const { rerender } = render(<ComponentName show={false} />)
    expect(screen.queryByTestId('content')).not.toBeInTheDocument()

    rerender(<ComponentName show={true} />)
    expect(screen.getByTestId('content')).toBeInTheDocument()
  })
})
```

**Coverage requirements:**
- Rendering with required props
- User interactions (clicks, form input, keyboard)
- Conditional display logic
- Prop variations (different states)

**Component testing rules:**
- Use `@testing-library/react` (already installed if Vitest configured)
- Use `screen` queries (getByRole, getByText, getByLabelText)
- Use `userEvent` for interactions (not `fireEvent`)
- Test behavior, not implementation details

#### Pattern D: API Routes

**Target:** Files in `app/api/` or `pages/api/` (Next.js)

**Test structure:**
```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { POST } from '../route'
import { prisma } from '@/lib/prisma'
import { getServerSession } from '@/lib/auth'

vi.mock('@/lib/prisma')
vi.mock('@/lib/auth')

describe('POST /api/endpoint', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should reject unauthenticated requests', async () => {
    vi.mocked(getServerSession).mockResolvedValue(null)

    const response = await POST(new Request('http://localhost', {
      method: 'POST',
      body: JSON.stringify({ data: 'value' })
    }))

    expect(response.status).toBe(401)
  })

  it('should validate request body', async () => {
    vi.mocked(getServerSession).mockResolvedValue({ user: { id: '1' } })

    const response = await POST(new Request('http://localhost', {
      method: 'POST',
      body: JSON.stringify({ invalid: 'data' })
    }))

    expect(response.status).toBe(400)
  })

  it('should process valid request', async () => {
    vi.mocked(getServerSession).mockResolvedValue({ user: { id: '1' } })
    vi.mocked(prisma.model.create).mockResolvedValue({ id: '1' })

    const response = await POST(new Request('http://localhost', {
      method: 'POST',
      body: JSON.stringify({ valid: 'data' })
    }))

    expect(response.status).toBe(200)
    expect(prisma.model.create).toHaveBeenCalledWith(
      expect.objectContaining({ data: expect.any(Object) })
    )
  })

  it('should handle database errors', async () => {
    vi.mocked(getServerSession).mockResolvedValue({ user: { id: '1' } })
    vi.mocked(prisma.model.create).mockRejectedValue(new Error('DB error'))

    const response = await POST(new Request('http://localhost', {
      method: 'POST',
      body: JSON.stringify({ valid: 'data' })
    }))

    expect(response.status).toBe(500)
  })
})
```

**Coverage requirements:**
- Unauthenticated request rejection
- Request validation (invalid body → 400)
- Auth checks (wrong user/role → 403)
- Success path (valid request → 200)
- Database errors (→ 500)

**API testing rules:**
- Mock Prisma: `vi.mock('@/lib/prisma')`
- Mock auth: `vi.mock('@/lib/auth')` or `vi.mock('next-auth')`
- Use `vi.clearAllMocks()` in `beforeEach`
- Create Request objects with proper method and body
- Test status codes AND response bodies

#### Pattern E: Encryption/Crypto Modules

**Target:** Files with `encrypt`, `decrypt`, `hash`, `crypto` in name or exports

**Test structure:**
```typescript
import { describe, it, expect } from 'vitest'
import { encrypt, decrypt } from '../encryption'

describe('encryption', () => {
  describe('round-trip', () => {
    it('should encrypt and decrypt to original value', () => {
      const original = 'sensitive data'
      const encrypted = encrypt(original)
      const decrypted = decrypt(encrypted)

      expect(decrypted).toBe(original)
    })

    it('should handle special characters', () => {
      const original = '!@#$%^&*(){}[]'
      const encrypted = encrypt(original)
      const decrypted = decrypt(encrypted)

      expect(decrypted).toBe(original)
    })

    it('should handle unicode', () => {
      const original = '你好世界 🔒'
      const encrypted = encrypt(original)
      const decrypted = decrypt(encrypted)

      expect(decrypted).toBe(original)
    })
  })

  describe('encryption properties', () => {
    it('should produce different output for same input', () => {
      const original = 'same value'
      const encrypted1 = encrypt(original)
      const encrypted2 = encrypt(original)

      // IVs should differ
      expect(encrypted1).not.toBe(encrypted2)
    })

    it('should produce non-readable output', () => {
      const original = 'plaintext'
      const encrypted = encrypt(original)

      expect(encrypted).not.toContain(original)
    })
  })

  describe('error handling', () => {
    it('should reject invalid encrypted data', () => {
      expect(() => decrypt('invalid')).toThrow()
    })
  })
})
```

**Coverage requirements:**
- Round-trip (encrypt → decrypt === original)
- Special characters and unicode
- Non-determinism (same input → different ciphertext due to IV)
- Invalid data rejection

### 5. Test File Placement

**Determine existing pattern:**
- Check if project has existing tests
- Use `Glob` to find `*.test.ts`, `*.spec.ts`, or `__tests__/` directories
- Identify the predominant pattern

**Patterns:**
```
Option A (colocated directory):
src/lib/encryption.ts
src/lib/__tests__/encryption.test.ts

Option B (adjacent file):
src/lib/encryption.ts
src/lib/encryption.test.ts

Option C (mirror structure):
src/lib/encryption.ts
tests/lib/encryption.test.ts
```

**Default:** If no existing tests found, use **Option A** (colocated `__tests__/` directory)

**Naming convention:**
- `[filename].test.ts` (Vitest standard)
- NOT `[filename].spec.ts` (use .test unless project already uses .spec)

### 6. Generate Test Files

For each target file:

1. **Read the source file** to understand:
   - Exported functions/components
   - Function signatures
   - Dependencies (imports)
   - Special patterns (Zod schemas, React hooks, API handlers)

2. **Determine pattern** (A/B/C/D/E from step 4)

3. **Generate test file** with:
   - Proper imports (Vitest utilities, source module)
   - Mock setup (if needed)
   - Test structure following the pattern
   - Placeholder assertions where specific implementation details are needed

4. **Write the test file** using the Write tool

5. **Track progress:**
   - Count files processed
   - Count tests generated
   - List any files skipped (and why)

### 7. Run Tests and Report

After generating all test files:

1. **Run the test suite:**
   ```bash
   npm test
   ```

2. **Parse output:**
   - Count total tests
   - Note passes and failures
   - Capture error messages for failures

3. **Fix common issues:**
   - Import path errors (adjust relative paths)
   - Missing type definitions (add proper types)
   - Mock configuration (adjust vi.mock paths)

4. **Re-run if fixes applied:**
   ```bash
   npm test
   ```

5. **Report to user:**
   ```
   ## Test Generation Complete

   **Files processed:** N
   **Test files created:** N
   **Total tests:** N
   **Status:** X passing, Y failing

   ### Created:
   - src/lib/__tests__/encryption.test.ts (5 tests)
   - src/lib/__tests__/validators.test.ts (12 tests)
   ...

   ### Failures:
   - `encryption.test.ts:42` — Mock configuration issue (fixed)

   Run `npm test` to execute all tests.
   Run `npm run test:watch` for watch mode.
   Run `npm run test:coverage` to see coverage report.
   ```

---

## Important Rules

### Vitest, NOT Jest
- Use `vi.fn()` and `vi.mock()` (Vitest API)
- Import from `'vitest'`, not `'@jest/globals'`
- Use `vi.clearAllMocks()`, not `jest.clearAllMocks()`

### No Semicolons
- Match project style (most Next.js projects omit semicolons)
- Check `package.json` or `.eslintrc` for confirmation

### Self-Contained Tests
- No shared mutable state between tests
- Use `beforeEach` to reset state
- Each `it` block should be independently runnable

### Descriptive Test Names
- Use `should` prefix: "should handle empty input"
- NOT: "handles empty input" or "empty input"
- Be specific about what's being tested

### Group by Function
- Use nested `describe` blocks by function name
- Top level: module/file name
- Second level: function/export name
- Third level: category (happy path, edge cases, errors)

### Mock External Deps
- ALWAYS mock Prisma in tests
- ALWAYS mock fetch/axios calls
- ALWAYS mock file system access
- NEVER make real network calls
- NEVER connect to real databases

### Test Every Field in Schemas
- For Zod schemas, test EVERY field
- One test per required field (missing → failure)
- One test per constraint (min/max/enum/format)
- Don't assume — verify each validation rule

### Encryption Round-Trip
- For encrypted data, test round-trip (encrypt → decrypt === original)
- Test with special characters and unicode
- Verify non-determinism (IV changes)

### Component Behavior, Not Implementation
- Test what the user sees and does
- NOT: "should call setState with value"
- YES: "should display success message after submission"

### No Placeholders in Critical Tests
- Tier 1 tests must be complete and executable
- Tier 2 tests can have TODOs for complex interaction flows
- Never leave empty test blocks (`it.todo()` is okay, empty `it()` is not)

---

## Error Handling

### If test runner not configured:
- Tell user to run `/devax-test-scaffold` first
- Do NOT attempt to configure test runner yourself
- Exit gracefully

### If source file not found:
- Report clearly which file was not found
- Show the full path attempted
- Exit for that file, continue with others if in batch mode

### If tests fail after generation:
- Attempt one round of fixes (imports, mocks, types)
- Re-run tests
- If still failing, report failures with enough context for user to fix
- Do NOT iterate endlessly trying to fix test failures

### If unsure of pattern:
- Default to Pattern A (utility/service)
- Add a TODO comment in the test file explaining what's needed
- Report to user that manual review is needed

---

## Quality Checklist

Before reporting completion, verify:

- [ ] All generated test files use Vitest (not Jest)
- [ ] All test files have proper imports
- [ ] No semicolons (if project style)
- [ ] All test blocks have descriptions starting with "should"
- [ ] All external deps are mocked
- [ ] All tests are in `describe` blocks
- [ ] Tier 1 tests are comprehensive (not just happy path)
- [ ] Test files are in correct location (matching existing pattern)
- [ ] Tests actually run (`npm test` executed)
- [ ] Report includes file list, test count, and pass/fail status
