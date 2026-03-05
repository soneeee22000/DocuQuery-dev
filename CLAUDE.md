# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DocuQuery is a resume-job match analysis platform for job seekers. Users upload a resume + job description and receive a match score (0-100), category breakdown (skills, experience, education, keywords), keyword gap analysis, and prioritized improvement tips.

**PRD (source of truth):** `docs/PRD.md` — every feature, endpoint, and component must trace back to a user story in the PRD.

## Stack

- **Backend:** FastAPI + Python 3.12 + SQLAlchemy + Alembic (migrations)
- **Frontend:** Next.js 16 (App Router) + TypeScript (strict) + Tailwind CSS
- **Database:** PostgreSQL 16 via Supabase
- **Auth:** Supabase Auth (JWT)
- **Storage:** Supabase Storage (resume/JD files)
- **AI/LLM:** OpenAI GPT-4o-mini (configurable — Claude API as alternative)
- **Testing:** pytest (backend), vitest (frontend), Playwright (E2E)

## Commands

```bash
# Backend
cd backend
uv run uvicorn app.main:app --reload          # Dev server (port 8000)
uv run pytest                                  # All tests
uv run pytest tests/services/test_analyzer.py  # Single test file
uv run pytest -k "test_match_score"            # Single test by name
uv run ruff check .                            # Lint
uv run ruff format .                           # Format
uv run mypy app/                               # Type check
uv run alembic upgrade head                    # Run migrations
uv run alembic revision --autogenerate -m "description"  # New migration

# Frontend
cd frontend
npm run dev                                    # Dev server (port 3000)
npm run test                                   # vitest
npm run test -- --run tests/components/MatchScore.test.tsx  # Single test
npm run lint                                   # ESLint + tsc --noEmit
npm run build                                  # Production build
npm run test:e2e                               # Playwright E2E tests (headless)
npm run test:e2e:ui                            # Playwright E2E tests (interactive UI)

# Full stack (Docker)
docker-compose up --build                      # All services
docker-compose up -d db                        # DB only
```

## Architecture

```
docuquery/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, middleware, exception handlers
│   │   ├── api/v1/              # Route handlers
│   │   │   ├── health.py        # GET /health
│   │   │   ├── auth.py          # /auth/* (register, login, refresh, me)
│   │   │   ├── documents.py     # /documents/* (upload, list, delete)
│   │   │   └── analysis.py      # /analysis/* (match, get, list, compare)
│   │   ├── services/            # Business logic
│   │   │   ├── parser.py        # PDF/DOCX/TXT text extraction
│   │   │   ├── analyzer.py      # LLM-powered match analysis (OpenAI)
│   │   │   ├── tips.py          # Tips prioritization + serialization
│   │   │   ├── user_service.py  # User CRUD
│   │   │   └── storage.py       # File storage (local, swappable)
│   │   ├── models/              # SQLAlchemy models (User, Document, Analysis)
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── core/                # Config, security, dependencies
│   │   └── utils/               # File validation helpers
│   ├── tests/                   # Mirrors app/ structure (59 tests)
│   ├── alembic/                 # DB migrations
│   └── pyproject.toml
├── frontend/
│   ├── src/app/                 # Next.js App Router pages
│   │   ├── (auth)/              # Login, register pages
│   │   └── (dashboard)/         # Protected: dashboard, documents, analysis, compare
│   ├── src/components/          # React components
│   │   ├── analysis/            # ScoreGauge, CategoryCard, TipsList, Skeleton, ScoreDeltaBanner, CategoryDeltaGrid
│   │   ├── documents/           # FileUpload, DocumentList, DeleteDialog
│   │   ├── auth/                # LoginForm, RegisterForm
│   │   ├── layout/              # Header, Sidebar
│   │   └── ui/                  # shadcn/ui primitives, EmptyState
│   ├── src/hooks/               # useAuth, useDocuments, useAnalysis*, useDashboardStats
│   ├── src/lib/                 # API client, auth, documents, analysis, score-utils
│   ├── src/types/               # TypeScript interfaces
│   ├── e2e/                     # Playwright E2E test specs
│   └── playwright.config.ts     # Playwright configuration
├── docs/
│   ├── PRD.md                   # Product requirements (source of truth)
│   └── ARCHITECTURE.md          # System design and data flows
└── docker-compose.yml
```

### Key Backend Services

- **`services/parser.py`** — Extracts text from PDF (PyMuPDF), DOCX (python-docx), TXT. Dispatches by MIME type.
- **`services/analyzer.py`** — Builds LLM prompt with resume + JD text (truncated to 8000/4000 chars), calls OpenAI GPT-4o-mini with JSON mode, retries once on timeout. Returns `(AnalysisResults, list[AnalysisTip])`.
- **`services/tips.py`** — `prioritize_tips()` sorts by priority, `tips_to_dicts()` serializes for JSON storage.
- **`services/user_service.py`** — User CRUD: get by email/id, create, authenticate.
- **`services/storage.py`** — `StorageService` ABC + `LocalStorageService` (uploads to disk). Swappable to Supabase Storage.

### API Response Format

All endpoints return consistent shape:

```json
{ "data": {}, "error": null, "meta": {} }
```

Error: `{"data": null, "error": {"code": "VALIDATION_ERROR", "message": "..."}}`

## Build Rules

1. **PRD is law** — if a feature is not in `docs/PRD.md`, do not build it
2. **Build in phase order** — complete Phase N gate before starting Phase N+1
3. **Test first** — write test file before implementation (TDD)
4. **One story at a time** — test → implement → verify → commit
5. **Types are mandatory** — strict mypy (Python), strict mode + no `any` (TypeScript)
6. **No dead code** — no console.log, no TODOs, no commented-out blocks in commits

## Environment Variables

See `.env.example` — required vars:

- `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_KEY`
- `OPENAI_API_KEY` (or `ANTHROPIC_API_KEY` if using Claude)
- `DATABASE_URL` (PostgreSQL connection string)
- `SECRET_KEY` (JWT signing)

## Git Conventions

- Conventional commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`
- No AI co-author tags or AI attribution in commits
- Squash merge feature branches
