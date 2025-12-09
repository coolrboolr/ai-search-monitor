# AI Search Monitor

A dedicated intelligence tool for tracking the "AI Search" and "search engineering" job market. It identifies market trends, potential clients (companies building internal AI search teams), and competitors (agencies selling these services).

## Features

- **Multi-Source Ingestion**:
  - **SEOJobs.com**: Targeted scraping of SEO-specific roles.
  - **LinkedIn**: Configurable multi-query search (e.g., "AI SEO", "Head of Search") using Playwright.
- **Intelligent Classification**:
  - **Role Tiers**: categorizes jobs into `Core AI Search`, `Related SEO`, or `Out of Scope` using semantic embeddings.
  - **Company Classification**: Distinguishes between **Clients** (Buyers) and **Competitors** (Agencies) using a hybrid heuristic + embedding approach.
  - **Industry Tagging**: Uses LLM (OpenAI) to tag companies with specific industries (e.g., "B2B SaaS", "Fintech").
- **Deduplication**: Robust deduplication using content hashing.
- **Dashboard**: React-based frontend to view and filter companies and jobs.

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy (Async), Pydantic, Playwright, SentenceTransformers.
- **Frontend**: Next.js 13+, TailwindCSS.
- **Database**: PostgreSQL.
- **AI**: OpenAI (GPT-4o-mini) for extraction, `all-MiniLM-L6-v2` for embeddings.

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL
- OpenAI API Key

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install .

playwright install chromium

# Configuration
cp .env.example .env
# Edit .env with DATABASE_URL and OPENAI_API_KEY (leave blank to disable LLM)

# Migrations
alembic upgrade head

# Run Server
uvicorn src.api.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Data Ingestion

To run the ingestion pipeline manually:

```bash
cd backend
export PYTHONPATH=$PYTHONPATH:.
python -m src.ingestion.pipeline
```
