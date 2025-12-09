# AI Search Monitor (v0)

AI Search Monitor tracks the hiring pulse of the AI search / SEO ecosystem.

It ingests job postings from curated sources, classifies them using semantic embeddings, and surfaces:

- Potential clients (SaaS / tools companies hiring AI search / SEO roles)
- Competitors (agencies / consultancies building in the same space)
- High-level analytics (company / role counts, last ingestion run)

## Architecture

- **Backend** (FastAPI + SQLAlchemy + Postgres + pgvector)
  - Async ingestion pipeline (`src/ingestion/pipeline.py`) pulling from SEOJobs.
  - Semantic relevance + company classification via `sentence-transformers/all-MiniLM-L6-v2`.
  - REST API:
    - `GET /api/companies` – companies with AI search roles, with counts & sample titles.
    - `GET /api/companies/{id}/jobs` – roles for a single company.
    - `GET /api/jobs` – global feed of AI search roles.
    - `GET /api/stats` – aggregate counts & last ingestion time.
- **Frontend** (Next.js App Router + Tailwind)
  - Dashboard with:
    - Stats bar: companies, roles, client / competitor split, last run.
    - Filterable companies table (tabs: Potential Clients vs Competitors).
    - Expandable rows with live job listings and “Apply” links.

## Local Setup

### Backend

```bash
cd backend
cp .env.example .env
# ensure Postgres is running and matches DATABASE_URL
uvicorn src.api.main:app --reload
```

Run ingestion:

```bash
cd backend
export PYTHONPATH=$PYTHONPATH:.
python -m src.ingestion.pipeline
```

Run tests:

```bash
cd backend
pytest
```

### Frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Demo Flow

1. Show stats bar: how many companies, roles, competitors, and last ingestion run.
2. In “Potential Clients”, filter by category and search for specific role types.
3. Expand a company row to show live AI search / SEO roles, and click through to the job posting.
4. Switch to “Competitors” and show how the system automatically classifies agencies vs SaaS.
