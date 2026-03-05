# Changelog

All notable changes to DocuQuery are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] - 2026-03-05

First production release. Full-stack resume-job match analysis platform.

### Added

**Phase 1 — Foundation**

- FastAPI backend with async SQLAlchemy, Pydantic schemas, Alembic migrations
- JWT auth system (bcrypt hashing, access/refresh tokens, protected routes)
- Document upload with text extraction (PDF via PyMuPDF, DOCX via python-docx, TXT)
- Magic byte file validation, 10MB size limit, MIME type checking
- Local file storage service (swappable to Supabase Storage)
- 33 pytest tests covering auth, documents, parser, and validation

**Phase 2 — Match Analysis**

- LLM-powered match analysis via OpenAI GPT-4o-mini (JSON mode, temp=0.2)
- Weighted scoring: skills 35%, experience 30%, education 15%, keywords 20%
- Keyword gap detection with per-category matched/missing breakdowns
- Prioritized improvement tips engine (max 5, ranked by impact)
- Pydantic validation of LLM JSON responses (AnalysisResults + AnalysisTip)
- Automatic retry on OpenAI timeout, rate limit error handling
- Analysis history list, detail view, and comparison endpoints
- Frontend: new analysis page, results page (ScoreGauge, CategoryCard, TipsList)
- Test suite expanded to 59 tests

**Phase 3 — Polish & Ship**

- Analysis comparison UI (checkbox select max 2, ScoreDeltaBanner, CategoryDeltaGrid)
- Dashboard with stats cards (total analyses, avg score, recent activity)
- Dark mode via `next-themes` with `useSyncExternalStore` hydration guard
- Toast notifications via `sonner` for all success/error feedback
- Skeleton loading screens, shared EmptyState component with contextual CTAs
- Responsive sidebar (desktop static, mobile overlay with hamburger toggle)
- 10 Playwright E2E tests (auth, documents, analysis, responsive, dark mode)
- Docker Compose setup (PostgreSQL + backend + frontend, auto-migration)
- GitHub Actions CI pipeline (ruff lint/format, pytest, ESLint, Next.js build)
- Deployed: Vercel (frontend) + Railway (backend)
