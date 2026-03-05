# DocuQuery Frontend

Next.js 16 (App Router) frontend for the DocuQuery resume-job match analysis platform. Built with React 19, TypeScript (strict), Tailwind CSS, and shadcn/ui.

## Development

```bash
npm install              # Install dependencies
npm run dev              # Dev server at http://localhost:3000
npm run build            # Production build
npm run lint             # ESLint + tsc --noEmit
npm run test             # Unit tests (vitest)
npm run test:e2e         # Playwright E2E tests (headless)
npm run test:e2e:ui      # Playwright E2E tests (interactive UI)
```

## Environment Setup

Copy `.env.example` to `.env.local` and fill in the required values:

- `NEXT_PUBLIC_API_URL` — Backend API base URL (default: `http://localhost:8000`)
- `NEXT_PUBLIC_SUPABASE_URL` — Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` — Supabase anonymous key

## Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── (auth)/             # Login, register
│   └── (dashboard)/        # Protected routes
│       ├── dashboard/      # Aggregate stats overview
│       ├── documents/      # Upload & manage documents
│       └── analysis/       # Analysis history, detail, new, compare
├── components/
│   ├── analysis/           # ScoreGauge, CategoryCard, TipsList, ScoreDeltaBanner, CategoryDeltaGrid
│   ├── documents/          # FileUpload, DocumentList, DeleteDialog
│   ├── auth/               # LoginForm, RegisterForm
│   ├── layout/             # Header, Sidebar
│   └── ui/                 # shadcn/ui primitives, EmptyState
├── hooks/                  # useAuth, useDocuments, useAnalysis*, useDashboardStats
├── lib/                    # API client, auth, documents, analysis utilities, score-utils
├── types/                  # TypeScript interfaces
e2e/                        # Playwright E2E test specs
playwright.config.ts        # Playwright configuration
```

## Full Project Documentation

See the [root README](../README.md) for backend setup, Docker Compose, architecture, and API docs.
