---
name: devax-test-scaffold
description: Set up Vitest + React Testing Library test infrastructure in any Next.js/TypeScript project. Detects framework, installs deps, creates config, verifies with sample test.
---

Set up Vitest + React Testing Library test infrastructure in any Next.js/TypeScript project.

## Usage
- `/devax-test-scaffold` — Run in the current project directory

## What it does

1. **Detect Project Context**
   - Read `package.json` to identify framework (Next.js, plain TS, etc.)
   - Read `CLAUDE.md` for project name
   - Check if test infrastructure already exists (vitest.config.ts, jest.config.ts, __tests__/ directories)
   - If tests already exist, report what's found and ask before proceeding

2. **Install Dependencies**
   ```bash
   npm install --save-dev vitest @vitejs/plugin-react @testing-library/react @testing-library/jest-dom @testing-library/user-event happy-dom
   ```

3. **Create vitest.config.ts**
   ```typescript
   import { defineConfig } from 'vitest/config'
   import path from 'path'

   export default defineConfig({
     test: {
       environment: 'happy-dom',
       include: ['src/**/*.test.{ts,tsx}'],
       globals: true,
     },
     resolve: {
       alias: {
         '@': path.resolve(__dirname, 'src'),
       },
     },
   })
   ```

4. **Add npm scripts to package.json**
   Add these scripts (don't overwrite existing):
   - `"test": "vitest run"`
   - `"test:watch": "vitest"`
   - `"test:coverage": "vitest run --coverage"`

5. **Create src/test-utils.tsx**
   Custom render wrapper with AllProviders placeholder:
   ```typescript
   import { render, RenderOptions } from '@testing-library/react'
   import { ReactElement } from 'react'

   // Placeholder for global providers (e.g., NextAuth SessionProvider, theme, etc.)
   function AllProviders({ children }: { children: React.ReactNode }) {
     return <>{children}</>
   }

   const customRender = (
     ui: ReactElement,
     options?: Omit<RenderOptions, 'wrapper'>
   ) => render(ui, { wrapper: AllProviders, ...options })

   export * from '@testing-library/react'
   export { customRender as render }
   ```

6. **Create src/__tests__/setup-verification.test.ts**
   Sample test to verify setup:
   ```typescript
   import { describe, it, expect } from 'vitest'

   describe('Test Infrastructure Setup', () => {
     it('should pass a basic test', () => {
       expect(true).toBe(true)
     })

     it('should handle basic math', () => {
       expect(1 + 1).toBe(2)
     })
   })
   ```

7. **Run and verify**
   ```bash
   npm test
   ```

8. **Update claude_docs/TESTING.md if it exists**
   - Set status to "Active"
   - Update test stack section with Vitest + RTL details
   - Add instructions for running tests

## Important

- Do NOT overwrite existing test configuration
- If `vitest.config.ts` already exists, show its contents and ask before replacing
- If `jest.config.ts` or other test configs exist, warn about potential conflicts
- The skill should work for any project with a `src/` directory and `package.json`
- After setup, remind the user to:
  - Update AllProviders in `test-utils.tsx` with actual providers
  - Add tests for priority modules listed in TESTING.md
