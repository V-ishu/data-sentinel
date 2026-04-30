# data-sentinel

![CI](https://github.com/V-ishu/data-sentinel/actions/workflows/ci.yml/badge.svg)

**Live demo:** [data-sentinel.onrender.com](https://data-sentinel.onrender.com) . 
**API docs:** [/docs](https://data-sentinel.onrender.com/docs)

> Open-source data validation service. Compare any two SQLAlchemy-compatible databases with a three-tier fallback strategy.

`data-sentinel` exposes both a Python CLI (Click) and a REST API (FastAPI) for verifying data integrity across database environments — useful during migrations, releases, and post-deploy validation.

---

## Why

During data migrations between environments (dev → UAT → prod, or one client's database to another), engineers routinely need to verify that the destination matches the source — table by table, row by row. Manual SQL queries are slow and error-prone. `data-sentinel` automates this with both a CLI for ad-hoc runs and a REST API for programmatic or scheduled use.

---

## Features

- **Three-tier comparison strategy** with automatic fallback:
  1. **Primary Key** — fast set-based comparison when a single PK exists
  2. **Composite Key** — multi-column key when no single PK is defined
  3. **MD5 Row Hash** — content-based fingerprinting when no key is available
- **REST API** — submit jobs, poll status, fetch results
- **Async job orchestration** — long comparisons don't block API responses
- **Persistent job history** — jobs survive server restarts
- **Configurable WHERE-clause filters** — compare a subset of rows
- **Dual interface** — original Click CLI is still fully supported alongside the HTTP API
- **Containerized** — single Dockerfile for cloud deployment
- **Auto-generated OpenAPI docs** at `/docs`

---

## Architecture

```
┌──────────────┐
│    Client    │  curl / Postman / browser at /docs
└──────┬───────┘
       │ HTTP
       ▼
┌──────────────────────────────────┐
│            FastAPI               │
│  POST /api/v1/comparisons        │
│  GET  /api/v1/comparisons        │
│  GET  /api/v1/comparisons/{id}   │
│  DELETE /api/v1/comparisons/{id} │
└──┬────────────────┬──────────────┘
   │ enqueue        │ persist job state
   ▼                ▼
┌───────────────┐  ┌──────────────┐
│ BackgroundTask│  │   Database   │
│  runs engine  │  │ (jobs table) │
└──────┬────────┘  └──────────────┘
       │ uses sentinel.* engine
       ▼
┌──────────────┐     ┌──────────────┐
│  Source DB   │     │  Target DB   │  user-supplied
└──────────────┘     └──────────────┘
```

---

## Quick Start

### Prerequisites

- Python 3.9+

### Run Locally

```bash
git clone https://github.com/V-ishu/data-sentinel.git
cd data-sentinel

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
python scripts/seed_demo.py  # creates source.db & target.db with intentional differences
uvicorn app.main:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) in a browser.

Try `POST /api/v1/comparisons` with this body:

```json
{
  "source_db": "sqlite:///source.db",
  "target_db": "sqlite:///target.db",
  "table": "employees"
}
```

You'll get a `job_id` back. Then call `GET /api/v1/comparisons/{job_id}` to see the full diff.

### CLI (Original)

```bash
python -m sentinel.cli compare \
  --source-db sqlite:///source.db \
  --target-db sqlite:///target.db \
  --table employees
```

---

## API Reference

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/v1/health` | Liveness check |
| `POST` | `/api/v1/comparisons` | Submit a new comparison job (returns `202 Accepted` with `job_id`) |
| `GET` | `/api/v1/comparisons` | List recent jobs |
| `GET` | `/api/v1/comparisons/{job_id}` | Get job status and full result |
| `DELETE` | `/api/v1/comparisons/{job_id}` | Delete a job |

Interactive docs available at `/docs` (Swagger UI) and `/redoc` (ReDoc).

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.9+ |
| REST API | FastAPI + Uvicorn |
| ORM | SQLAlchemy 2.0 |
| Validation | Pydantic v2 + pydantic-settings |
| Database | PostgreSQL (production) / SQLite (local dev) |
| CLI | Click |
| Container | Docker |

---

## Project Structure

```
data-sentinel/
├── app/                    # FastAPI service layer
│   ├── api/v1/             # HTTP routes
│   ├── core/               # Config (pydantic-settings)
│   ├── db/                 # SQLAlchemy session + ORM models
│   ├── schemas/            # Pydantic request/response models
│   ├── services/           # Business logic + job orchestration
│   └── main.py             # FastAPI app entry point
├── sentinel/               # Original comparison engine + Click CLI
│   ├── comparator.py
│   ├── connector.py
│   ├── reporter.py
│   └── cli.py
├── scripts/
│   └── seed_demo.py        # Seeds demo SQLite DBs with intentional differences
├── Dockerfile              # Production container
├── requirements.txt
└── README.md
```

---

## Configuration

All config is read from environment variables or a local `.env` file.

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./data_sentinel.db` | SQLAlchemy connection URL for the metadata store |

See `.env.example` for the full format.

---

## Roadmap

- [x] FastAPI REST layer over the existing CLI engine
- [x] Persistent job storage with SQLAlchemy ORM
- [x] Async job orchestration via FastAPI BackgroundTasks
- [x] Env-driven configuration + Dockerfile for cloud deployment
- [x] Production deployment on Render
- [x] Pytest test suite + GitHub Actions CI
- [ ] Excel report download endpoint (currently CLI-only)
- [ ] Optional API key authentication
- [ ] Migrate background jobs to Celery for distributed workers

---

## License

MIT