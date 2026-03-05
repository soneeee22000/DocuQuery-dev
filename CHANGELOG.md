# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-05

### Added

- **Phase 1 — Auth & Documents:** User registration/login (Supabase Auth, JWT), document upload with PDF/DOCX/TXT text extraction, file validation, local storage service
- **Phase 2 — Match Analysis:** LLM-powered resume-job match scoring (OpenAI GPT-4o-mini), category breakdown (skills, experience, education, keywords), keyword gap analysis, prioritized improvement tips, analysis history and detail views
- **Phase 3 — Polish & UX:** Dark mode (next-themes, class-based), toast notifications (sonner), loading skeletons, empty states, dashboard with aggregate stats, side-by-side analysis comparison with delta indicators, responsive sidebar (desktop static + mobile overlay), 10 Playwright E2E tests, Docker Compose setup, GitHub Actions CI pipeline
