# Compliance Centras

## Architecture
- Backend: FastAPI (Python 3.12)
- Database: SQLAlchemy (supporting PostgreSQL + pgvector and SQLite fallback)
- Frontend: Single Page Application (SPA) with Vanilla HTML5, JS, and CSS served by FastAPI, providing a rich, premium, dark-mode user interface.
- AI Layer: Gemini 3.1 Flash Lite API via google-genai SDK.
- Parser Layer: Pluggable Document Parser (using Docling if available, with BeautifulSoup4/PyPDF/docx fallbacks).

## Module Registry
| Module | Path | Responsibility | Depends on | Depended on by |
|--------|------|----------------|------------|----------------|
| Backend | `/app/main.py` | FastAPI application, API routers, static mounting, healthcheck, security headers | DB, Agents | Frontend |
| Models | `/app/models.py` | SQLAlchemy database models | None | Backend, DB |
| Database | `/app/database.py` | Database session management, connection pooling, and similarity search | Models | Backend, Agents |
| Monitoring | `/app/agents/monitoring.py` | Automated daily checks and SHA256 hashing | Database, Parser | Backend |
| Parsing | `/app/agents/parsing.py` | Pluggable parsing to Markdown & HTML tables (Docling/BeautifulSoup/PyPDF) | None | Monitoring, Backend |
| Legal | `/app/agents/legal.py` | Gemini-based comparison and legal risk analysis | AI Client | Backend, Workflow |
| Knowledge | `/app/agents/knowledge.py` | Vector-based search of internal policies | Database | Backend, Workflow |
| Impact/Draft/Review | `/app/agents/document.py` | Impact analysis, drafts generation, review | AI Client, Database | Backend |
| Notifications | `/app/agents/notifications.py` | In-app alerts, quality warnings, external webhooks | Database, Models | Backend, Scheduler |
| Scheduler | `/app/scheduler.py` | Automated background monitoring and periodic checks | Monitoring, Notifications | Backend (Lifespan) |
| Frontend UI | `/static` | Beautiful SPA UI with HSL colors, dark mode, graph visualization | Backend APIs | Browser |

## Decisions Log
| # | Date | Decision | Context | Alternatives rejected | Reversal cost |
|---|------|----------|---------|-----------------------|---------------|
| 1 | 2026-07-10 | Single Page Web App (SPA) | We will build a unified dashboard instead of a raw Open WebUI container to make local setup zero-config. | Dockerized Open WebUI customization | Low (UI is decoupleable from API) |
| 2 | 2026-07-10 | SQLite + SQL similarity fallback | Allow database execution without requiring a running PostgreSQL server, while maintaining pgvector schema compatibility. | Pure pgvector (would crash on default dev machine) | Medium |
| 3 | 2026-07-10 | Pluggable Document Parser | Avoid installing the heavy `docling` package if CPU/local resources are constrained; fall back to standard Python libraries. | Strict Docling-only parsing | Low |
| 4 | 2026-07-10 | FastAPI lifespan context | Migrate from deprecated @app.on_event("startup") to async lifespan. | Deprecated on_event | Low |
| 5 | 2026-08-18 | Background Async Scheduler & Notifications | Automated scheduled monitoring loop with in-app alerts, quality gates, and Webhook/Telegram dispatch. | Manual cron/external trigger only | Low |
| 6 | 2026-08-18 | Production Hardening & Security | Security headers, CORS configuration, non-root Docker, healthcheck `/healthz`, PostgreSQL connection pooling. | Unhardened production deployment | Low |

## Task Log
| # | Task | Mode | Status | Files | Goals satisfied (G1–G4) | Notes |
|---|------|------|--------|-------|-------------------------|-------|
| 1 | Create basic structure, backend and frontend | Feature | Completed | app/*, static/*, run.py, requirements.txt, tests/* | G1, G2, G3, G4 | Initial MVP+ implementation completed and fully verified |
| 2 | Code review & Best practices fixes | Refactor | Completed | app/main.py, static/app.js, agents/*.py | G2, G3 | Fixed JS TypeError, migrated to lifespan, updated models to gemini-3.1-flash-lite |
| 3 | Architectural Audit (Grill Me) & Premium UX/UI Redesign | Feature/Fix | Completed | app/agents/document.py, static/app.css, static/app.js, static/index.html | G1, G2, G3 | Fixed Corporate Memory AI loop (decisions are now injected into prompt), replaced generic CSS with Premium Glassmorphism UI, added Toast notifications. |
| 4 | Authentication (JWT) & Docker Deployment | Feature | Completed | app/auth.py, app/main.py, app/models.py, app/database.py, Dockerfile, docker-compose.yml | G1, G3, G4 | Added JWT auth, protected all API endpoints, seeded admin@cic.kz, built Premium Login UI, created Docker infrastructure with PostgreSQL (pgvector). |
| 5 | Scheduled Monitoring, Notifications & Best Practice Hardening | Feature/Audit | Completed | app/scheduler.py, app/agents/notifications.py, app/agents/document.py, app/main.py, static/*, tests/* | G1, G2, G3, G4 | Added background async scheduler, in-app notification center, quality gate alerts, hardened docx exports and LLM normalizers, 100% test coverage. |
| 6 | Production Release & Hardening | Feature/Hardening | Completed | app/main.py, app/database.py, run.py, Dockerfile, docker-compose.yml, .env.example, static/*, tests/* | G1, G2, G3, G4 | Added /healthz, Security Headers, CORS, PostgreSQL connection pooling, non-root user appuser in Docker, healthchecks, and 14 tests (100% pass). |

## Build & Test Commands
- Run backend: `python run.py` or `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Run Docker: `docker-compose up -d --build`
- Test commands: `pytest -v`
