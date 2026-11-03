# AdaptiveAI — Backend

> Multi-tenant enterprise conversational AI platform with RAG, confidence checking, and continuous improvement via human-verified feedback loops.

## Prerequisites

| Tool | Version |
|---|---|
| Python | ≥ 3.11 |
| PostgreSQL | ≥ 16 with pgvector extension |
| pip / uv | latest |

---

## Quick Start

### 1. Clone & set up the environment

```bash
cd adaptive-ai
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -e ".[dev]"
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env — set your DB credentials, API keys, and SECRET_KEY
```

### 3. Set up PostgreSQL + pgvector

```sql
-- Run as postgres superuser:
CREATE DATABASE adaptiveai;
CREATE USER adaptiveai_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE adaptiveai TO adaptiveai_user;

-- Connect to the adaptiveai DB then:
CREATE EXTENSION IF NOT EXISTS vector;
```

### 4. Run Alembic migrations

```bash
# Generate the initial migration from models:
alembic revision --autogenerate -m "initial_schema"

# Apply migrations:
alembic upgrade head
```

### 5. Start the development server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000/docs** for the interactive Swagger UI.

---

## Project Structure

```
adaptive-ai/
├── alembic/                   # DB migrations
├── app/
│   ├── main.py                # FastAPI app factory + lifespan
│   ├── config.py              # Pydantic settings (all env vars)
│   ├── core/
│   │   ├── security.py        # JWT + bcrypt
│   │   ├── dependencies.py    # Auth + tenant FastAPI deps
│   │   └── exceptions.py      # Typed HTTP exceptions
│   ├── db/
│   │   ├── base.py            # Declarative base + mixins
│   │   ├── session.py         # Async engine + session dep
│   │   └── init_db.py         # Startup seeder (pgvector + super admin)
│   ├── models/                # SQLAlchemy ORM models
│   │   ├── company.py         # Tenant root
│   │   ├── user.py            # Users + roles
│   │   ├── document.py        # Uploaded files
│   │   ├── document_chunk.py  # pgvector chunks
│   │   ├── knowledge_item.py  # Verified knowledge entries
│   │   ├── conversation.py    # Chat sessions
│   │   ├── message.py         # Chat turns (RAG provenance)
│   │   ├── feedback.py        # User ratings
│   │   ├── experience.py      # Adaptive learning store
│   │   ├── escalation.py      # Human handoff records
│   │   ├── chatbot_settings.py# Per-company personality config
│   │   └── audit_log.py       # Immutable audit trail
│   ├── ai/
│   │   └── providers/
│   │       ├── base.py        # Abstract LLMProvider + EmbeddingProvider
│   │       ├── openai_provider.py
│   │       ├── gemini_provider.py
│   │       └── anthropic_provider.py
│   └── api/v1/                # REST endpoints (§32)
│       ├── auth.py
│       ├── companies.py
│       ├── users.py
│       ├── documents.py
│       ├── knowledge.py
│       ├── chat.py
│       ├── feedback.py
│       ├── experiences.py
│       ├── escalations.py
│       └── analytics.py
└── tests/
```

---

## Switching AI Providers

No code changes needed — edit `.env`:

```env
# Use Gemini instead of OpenAI:
AI_PROVIDER=gemini
EMBEDDING_PROVIDER=gemini
GEMINI_API_KEY=your-key-here

# Use Anthropic for LLM, OpenAI for embeddings:
AI_PROVIDER=anthropic
EMBEDDING_PROVIDER=openai
```

---

## Multi-Tenant Isolation

Every tenant-scoped table carries a `company_id` FK enforced at 3 layers:

1. **JWT** — `company_id` embedded in access token payload
2. **FastAPI Dependency** — `get_tenant_id()` extracts and validates it on every request
3. **ORM** — `TenantMixin` makes `company_id` a required column, services always filter by it

---

## Key Environment Variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | JWT signing secret (use `openssl rand -hex 32`) |
| `AI_PROVIDER` | LLM provider: `openai` \| `gemini` \| `anthropic` |
| `EMBEDDING_PROVIDER` | Embedding provider (can differ from LLM) |
| `CONFIDENCE_HIGH_THRESHOLD` | Min score for high-confidence responses (default: 0.80) |
| `CONFIDENCE_LOW_THRESHOLD` | Below this triggers escalation (default: 0.50) |

---

## Development

```bash
# Run tests
pytest

# Lint + format
ruff check .
ruff format .

# Type check
mypy app/
```

---

## Roadmap (MVP Phases per §50)

- [x] **Phase 0** — Project scaffold, DB models, AI provider abstraction
- [ ] **Phase 1** — Auth, company registration, multi-tenancy enforcement
- [ ] **Phase 2** — Document upload, text extraction, chunking, embeddings
- [ ] **Phase 3** — Chat API, RAG pipeline, conversation memory
- [ ] **Phase 4** — Feedback, experience memory, human correction workflow
- [ ] **Phase 5** — Analytics dashboard, accuracy metrics
- [ ] **Phase 6** — Human support, multilingual, voice, external APIs
