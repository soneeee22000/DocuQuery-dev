# DocuQuery — Architecture

## System Design

DocuQuery is a **resume-job match analysis platform** built as a decoupled fullstack application: a FastAPI backend serving REST APIs and a Next.js frontend with server-side rendering.

### Design Principles

1. **Clean separation** — API routes delegate to services; no business logic in route handlers
2. **Type safety everywhere** — Pydantic (backend) + TypeScript strict mode (frontend)
3. **LLM-agnostic** — analyzer service uses an abstraction layer; swap OpenAI for Claude via config
4. **Structured AI output** — LLM returns JSON matching a Pydantic schema; parse and validate before storing
5. **Stateless backend** — JWT auth, no server sessions; scales horizontally

## Architecture Diagram

> **[View interactive System Architecture on Excalidraw](https://excalidraw.com/#json=BSZhDGDr5Qm3eDInxF8E8,EFSiUD4_xVdstYVDt2oipA)** | **[View Match Analysis Flow](https://excalidraw.com/#json=Nuok9iHjYoT326RfiCf-B,9D9-jQvlv29quAIuccmsOw)**

```
                    ┌─────────────────────────────────────────────┐
                    │              Frontend (Vercel)              │
                    │  Next.js 16 · TypeScript · Tailwind · shadcn│
                    └──────────────────┬──────────────────────────┘
                                       │ REST API
                    ┌──────────────────▼──────────────────────────┐
                    │              Backend (Railway)              │
                    │  FastAPI · Python 3.12 · SQLAlchemy · JWT   │
                    │                                             │
                    │  ┌──────────┐ ┌────────────┐ ┌───────────┐ │
                    │  │Doc Parser│ │Match Analyz.│ │Tips Engine│ │
                    │  └──────────┘ └──────┬─────┘ └───────────┘ │
                    └──────────┬───────────┼──────────────────────┘
                               │           │
                    ┌──────────▼──┐  ┌─────▼──────────┐
                    │ PostgreSQL  │  │ OpenAI         │
                    │ (Supabase)  │  │ GPT-4o-mini    │
                    └─────────────┘  └────────────────┘
```

## Data Model

Three SQLAlchemy models share `UUIDPrimaryKeyMixin` (UUID pk) and `TimestampMixin` (created_at, updated_at).

```
users
├── id          UUID PK
├── email       VARCHAR(320) UNIQUE
├── hashed_password VARCHAR(128)
├── created_at  TIMESTAMPTZ
└── updated_at  TIMESTAMPTZ

documents
├── id              UUID PK
├── user_id         UUID FK → users.id ON DELETE CASCADE (indexed)
├── name            VARCHAR(255)
├── doc_type        ENUM('resume', 'job_description')
├── mime_type       VARCHAR(100)
├── file_url        VARCHAR(500)
├── file_size       INTEGER
├── extracted_text  TEXT (nullable)
├── created_at      TIMESTAMPTZ
└── updated_at      TIMESTAMPTZ

analyses
├── id          UUID PK
├── user_id     UUID FK → users.id ON DELETE CASCADE (indexed)
├── resume_id   UUID FK → documents.id ON DELETE CASCADE
├── jd_id       UUID FK → documents.id ON DELETE CASCADE
├── score       INTEGER (0-100)
├── results     JSON — category scores, matched/missing items
├── tips        JSON — prioritized improvement tips
├── llm_model   VARCHAR(100) — model used (default: gpt-4o-mini)
├── created_at  TIMESTAMPTZ
└── updated_at  TIMESTAMPTZ
```

Note: JSON columns (not JSONB) are used for SQLite test compatibility. Production PostgreSQL handles both.

### Analysis `results` JSON Structure

```json
{
  "score": 78,
  "categories": {
    "skills": {
      "score": 85,
      "matched": ["Python", "React"],
      "missing": ["Kubernetes"],
      "feedback": "Strong technical skills, missing container orchestration."
    },
    "experience": {
      "score": 70,
      "matched": ["3 years backend"],
      "missing": ["team lead"],
      "feedback": "3/5 years required. Highlight relevant projects."
    },
    "education": {
      "score": 90,
      "matched": ["Master's CS"],
      "missing": [],
      "feedback": "Master's degree exceeds requirement."
    },
    "keywords": {
      "score": 65,
      "matched": ["API", "REST", "microservices"],
      "missing": ["CI/CD", "Agile"],
      "feedback": "Good keyword coverage, missing DevOps terms."
    }
  },
  "keyword_gaps": ["Kubernetes", "CI/CD", "Agile"]
}
```

### Analysis `tips` JSON Structure

```json
[
  {
    "priority": 1,
    "category": "skills",
    "suggestion": "Add Kubernetes experience from side projects",
    "section": "Skills"
  },
  {
    "priority": 2,
    "category": "keywords",
    "suggestion": "Include 'CI/CD' in your DevOps section",
    "section": "Experience"
  }
]
```

Scoring weights: skills 35%, experience 30%, education 15%, keywords 20%. Each category has `score`, `matched`, `missing`, and `feedback`. Tips are limited to 5, ordered by priority.

## Data Flows

### Document Upload Flow

```
1. User selects PDF/DOCX/TXT file in frontend
2. Frontend validates file type + size (<10MB) client-side
3. POST /api/v1/documents/upload (multipart form: file + doc_type)
4. Backend validates file (magic bytes check, size, extension → MIME)
5. Extract text: PDF → PyMuPDF, DOCX → python-docx, TXT → UTF-8/latin-1
6. Upload to local storage (uploads/{user_id}/{uuid}_{filename})
7. Store Document record with extracted_text in DB
8. Return DocumentResponse to frontend
```

### Match Analysis Flow

```
1. User selects resume + JD from dropdowns on /analysis/new
2. POST /api/v1/analysis/match { resume_id, jd_id }
3. Backend validates: doc ownership, doc_type match, extracted_text exists
4. Truncate texts (resume: 8000 chars, JD: 4000 chars)
5. Build system prompt with scoring weights + JSON schema
6. Call OpenAI GPT-4o-mini with response_format=json_object, temp=0.2
7. Retry once on timeout; raise AppError on double-timeout or rate limit
8. Parse JSON → AnalysisResults + list[AnalysisTip] via Pydantic
9. Prioritize tips, store Analysis record (score, results JSON, tips JSON)
10. Return AnalysisResponse (includes resume_name, jd_name) to frontend
```

### Analysis Comparison Flow

```
1. User uploads revised resume, triggers new analysis against same JD
2. GET /api/v1/analysis/{new_id}/compare/{prev_id}
3. Backend fetches both analyses
4. Compute deltas: overall score change, per-category changes
5. Identify: gaps addressed, gaps remaining, new gaps (if any)
6. Return comparison object to frontend
```

## Key Technical Decisions

| Decision          | Choice                  | Rationale                                              |
| ----------------- | ----------------------- | ------------------------------------------------------ |
| Backend framework | FastAPI                 | Async-first, Pydantic native, fast for AI workloads    |
| Database          | PostgreSQL (Supabase)   | JSONB for flexible analysis results, free managed tier |
| Auth              | Supabase Auth           | Zero auth code to maintain, JWT out of the box         |
| File storage      | Supabase Storage        | Integrated with auth, signed URLs for security         |
| LLM               | OpenAI GPT-4o-mini      | Cost-effective, JSON mode, fast; Claude as fallback    |
| PDF parsing       | PyMuPDF                 | Fast, reliable, page-level extraction                  |
| Frontend          | Next.js 16 (App Router) | SSR, file-based routing, React 19 support              |
| Migrations        | Alembic                 | SQLAlchemy-native, version-controlled schema changes   |
| Dark mode         | next-themes             | System preference detection, class-based toggle        |
| Toasts            | sonner                  | Lightweight, accessible toast notifications            |
| E2E testing       | Playwright              | Cross-browser, mobile viewports, network mocking       |
| UI components     | shadcn/ui               | Copy-paste primitives, fully customizable, Tailwind    |

## Frontend Architecture

### Pages & Routes (Next.js App Router)

| Route               | Page             | Purpose                                     |
| ------------------- | ---------------- | ------------------------------------------- |
| `/login`            | Login page       | Email + password login                      |
| `/register`         | Register page    | New user registration                       |
| `/dashboard`        | Dashboard        | Stats cards, quick actions, recent activity |
| `/documents`        | Documents        | Upload (drag-and-drop) + list with delete   |
| `/analysis`         | Analysis History | Past analyses with checkbox comparison      |
| `/analysis/new`     | New Analysis     | Select resume + JD, trigger analysis        |
| `/analysis/[id]`    | Analysis Results | Score gauge, category cards, tips list      |
| `/analysis/compare` | Comparison       | Score delta banner + category delta grid    |

### Key Frontend Patterns

- **Hooks pattern:** `useAuth`, `useDocuments`, `useAnalysisHistory`, `useAnalysisTrigger`, `useAnalysis`, `useComparison`, `useDashboardStats`
- **Toast notifications:** All errors/success via `sonner` (`toast.error()`, `toast.success()`) — no inline error `<p>` elements
- **Dark mode:** `next-themes` ThemeProvider with `attribute="class"`, `defaultTheme="system"`. Toggle in header using `useSyncExternalStore` for hydration safety.
- **Responsive sidebar:** Desktop static (`md:block`), mobile overlay with backdrop + hamburger toggle (`md:hidden`)
- **Shared utilities:** `lib/score-utils.ts` (`getScoreVariant`, `formatDate`), `components/ui/empty-state.tsx`
- **Comparison flow:** Checkbox select (max 2) on history page → auto-sort by date → navigate to `/analysis/compare?current=ID&previous=ID`

### Component Library

Built on shadcn/ui primitives (`Card`, `Button`, `Badge`, `Skeleton`, `Select`, `Separator`, `Dialog`, `Toaster`).

Custom analysis components:

- `ScoreGauge` — SVG circle gauge with color-coded score overlay
- `CategoryCard` — Score + matched/missing lists + feedback
- `TipsList` — Prioritized improvement tips
- `ScoreDeltaBanner` — Large delta number with up/down arrow
- `CategoryDeltaGrid` — 2x2 grid of per-category deltas
- `AnalysisSkeleton` — Loading skeleton for analysis pages
- `EmptyState` — Shared empty state with optional CTA action

## Testing Infrastructure

### Backend (59 tests)

- **Framework:** pytest + aiosqlite (SQLite for test isolation)
- **Pattern:** `autouse=True` fixture creates/drops tables per test; OpenAI mocked via `@patch`
- **Coverage:** Auth endpoints, document CRUD, analysis lifecycle, parser service, tips service, file validation

### Frontend E2E (10 Playwright tests)

- **Config:** Desktop Chrome + iPhone 14 projects, dev server auto-start
- **Specs:** `auth.spec.ts` (4), `documents.spec.ts` (2), `analysis.spec.ts` (2), `responsive.spec.ts` (2)
- **Helpers:** `registerUser()`, `loginAs()` in `e2e/helpers/auth.ts`
- **LLM mocking:** `page.route()` intercepts analysis API for deterministic tests

## Docker Compose

```yaml
services:
  db: PostgreSQL 16 Alpine, healthcheck, pgdata volume
  backend: Runs "alembic upgrade head && uvicorn ..." on start
  frontend: Next.js on port 3000, NEXT_PUBLIC_API_URL=http://localhost:8000
```

Migrations run automatically before the backend starts — no manual `alembic upgrade` needed.

## v2 Considerations (In-App Resume Editor)

The architecture is designed to support a future in-app editor:

- `extracted_text` is stored on documents — can be loaded into an editor
- Analysis `tips` reference specific categories — can map to resume sections
- `results.categories` identify exact missing keywords — can power inline suggestions
- Comparison flow already supports before/after tracking
