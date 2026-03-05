# DocuQuery — Resume-Job Match Analyzer

Upload your resume and a job description. Get an instant **match score**, **keyword gap analysis**, **section-by-section feedback**, and **actionable tips** to improve your chances — powered by AI.

## Why This Exists

Job seekers waste hours manually comparing resumes to job descriptions, missing keyword gaps and failing to tailor applications effectively. DocuQuery provides structured, AI-powered match analysis so you know exactly what to fix before you apply.

## Tech Stack

| Layer        | Technology                                        |
| ------------ | ------------------------------------------------- |
| **Frontend** | Next.js 15 (App Router), TypeScript, Tailwind CSS |
| **Backend**  | FastAPI, Python 3.12, SQLAlchemy, Alembic         |
| **Database** | PostgreSQL 16 (Supabase)                          |
| **Auth**     | Supabase Auth (JWT)                               |
| **Storage**  | Supabase Storage (file uploads)                   |
| **AI/LLM**   | OpenAI GPT-4o-mini (configurable)                 |
| **Testing**  | pytest, vitest, Playwright                        |
| **DevOps**   | Docker, GitHub Actions, Vercel, Railway           |

## Features

- **Match Analysis** — Upload resume + JD, get a 0-100 match score with category breakdown (skills, experience, education, keywords)
- **Keyword Gap Detection** — See exactly which keywords are missing from your resume
- **Actionable Tips** — Prioritized suggestions on what to change, referencing specific resume sections
- **Analysis History** — Track past analyses, compare scores after revisions
- **Document Management** — Upload, list, and re-use resumes and job descriptions
- **Score Comparison** — Re-upload a revised resume and see your improvement

## Getting Started

### Prerequisites

- Python 3.12+ and [uv](https://docs.astral.sh/uv/)
- Node.js 20+ and npm
- Docker and Docker Compose (for PostgreSQL)
- Supabase account (free tier works)
- OpenAI API key

### Backend Setup

```bash
cd backend
uv sync
cp .env.example .env
# Fill in Supabase and OpenAI credentials

uv run alembic upgrade head      # Run migrations
uv run uvicorn app.main:app --reload  # Start dev server (port 8000)
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
# Fill in Supabase and API URLs

npm run dev  # Start dev server (port 3000)
```

### Run with Docker

```bash
docker-compose up --build
```

## API Endpoints

| Method   | Endpoint                                  | Description                        |
| -------- | ----------------------------------------- | ---------------------------------- |
| `POST`   | `/api/v1/auth/register`                   | Register new user                  |
| `POST`   | `/api/v1/auth/login`                      | Login, return JWT                  |
| `POST`   | `/api/v1/documents/upload`                | Upload resume or JD (PDF/DOCX/TXT) |
| `GET`    | `/api/v1/documents`                       | List user's documents              |
| `DELETE` | `/api/v1/documents/{id}`                  | Delete a document                  |
| `POST`   | `/api/v1/analysis/match`                  | Trigger match analysis             |
| `GET`    | `/api/v1/analysis/{id}`                   | Get analysis result                |
| `GET`    | `/api/v1/analysis`                        | List past analyses                 |
| `GET`    | `/api/v1/analysis/{id}/compare/{prev_id}` | Compare two analyses               |

## Project Structure

```
docuquery/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/v1/          # Route handlers
│   │   ├── services/        # Business logic (parser, analyzer, tips)
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── core/            # Config, security, deps
│   ├── tests/
│   └── alembic/             # DB migrations
├── frontend/                # Next.js application
│   └── src/
│       ├── app/             # App Router pages
│       ├── components/      # React components
│       ├── lib/             # API client, utils
│       └── types/           # TypeScript interfaces
├── docs/
│   ├── PRD.md               # Product requirements (source of truth)
│   └── ARCHITECTURE.md      # System design and data flows
├── CLAUDE.md                # Claude Code guidance
└── docker-compose.yml
```

## Documentation

- **[PRD](docs/PRD.md)** — Product requirements, user stories, acceptance criteria
- **[Architecture](docs/ARCHITECTURE.md)** — System design, data models, data flows
- **[CLAUDE.md](CLAUDE.md)** — Development commands, build rules, conventions

## Build Status

| Phase | Description                                                          | Status |
| ----- | -------------------------------------------------------------------- | ------ |
| 1     | Foundation (auth, upload, extraction, CI)                            | Done   |
| 2     | Core feature — match analysis (LLM, API, UI)                         | Done   |
| 3     | Polish, iterate & ship (comparison UI, E2E, dark mode, Docker, docs) | Next   |

**Backend:** 59 tests passing | **Frontend:** TypeScript strict, builds clean

## Roadmap

- **v1 (current):** Match analysis, keyword gaps, tips, history, comparison
- **v2:** In-app resume editor — apply AI tips and edit your resume directly, then re-analyze

## License

MIT
