# Deployment Guide: AI Search Monitor

This guide covers deploying the **AI Search Monitor** using the "Render + Supabase + Vercel" stack.

Prerequisites:
- GitHub account (repo pushed)
- Render account
- Supabase account (or use Render Postgres)
- Vercel account (optional, for Frontend)

---

## 1. Database (Supabase)

1.  Create a new Project on [Supabase](https://supabase.com).
2.  Go to the **SQL Editor** in the side bar.
3.  Run: `create extension if not exists vector;`
4.  Go to **Project Settings** -> **Database**.
5.  Copy the **Connection String (URI Mode)**. It looks like: `postgresql://postgres.[ref]:[password]@aws-0-us-west-1.pooler.supabase.com:6543/postgres`
    *   *Keep this safe, you'll need it for Render.*

---

## 2. Backend (Render)

### A. Web Service (The API)
1.  Create a **New Web Service** on [Render](https://dashboard.render.com).
2.  Connect your GitHub repository.
3.  **Root Directory**: `backend`
4.  **Runtime**: Docker
5.  **Environment Variables**:
    *   `DATABASE_URL`: (Paste your Supabase connection string)
    *   `OPENAI_API_KEY`: (Your OpenAI Key)
    *   `INGEST_MAX_UPSERT_CONCURRENCY`: `8` (Optional tuning)
6.  Click **Create Web Service**.
    *   *Note the URL Render gives you (e.g., `https://algo-monitor-backend.onrender.com`).*

### B. Cron Job (The Ingestion Pipeline)
1.  Create a **New Cron Job** on Render using the **same repo**.
2.  **Root Directory**: `backend`
3.  **Runtime**: Docker
4.  **Schedule**: `0 */8 * * *` (Every 8 hours)
5.  **Command**: `python -m src.ingestion.pipeline`  *(Note: The Dockerfile default CMD is the web server, but Render Cron lets you override the command)*.
6.  **Environment Variables**:
    *   Add the **Exact Same** variables as the Web Service (`DATABASE_URL`, `OPENAI_API_KEY`, etc.).
7.  Click **Create Cron Job**.

---

## 3. Frontend (Vercel or Render)

### Option A: Vercel (Recommended for Next.js)
1.  Import your repo project in [Vercel](https://vercel.com).
2.  **Root Directory**: `frontend` (Edit the root directory settings if needed).
3.  **Framework Preset**: Next.js (Should auto-detect).
4.  **Environment Variables**:
    *   `NEXT_PUBLIC_API_URL`: `https://[YOUR-RENDER-BACKEND-NAME].onrender.com` (No trailing slash)
5.  Deploy.

### Option B: Render Static Site
1.  Create a **New Static Site** on Render.
2.  **Root Directory**: `frontend`
3.  **Build Command**: `npm install && npm run build`
4.  **Publish Directory**: `.next` or `out` (You may need to configure `next.config.js` for strict static export if using `out`). *Vercel is easier for Next.js hybrid apps.*
5.  **Environment Variables**:
    *   `NEXT_PUBLIC_API_URL`: `https://[YOUR-RENDER-BACKEND-NAME].onrender.com`

---

## 4. Verification

1.  Visit your Frontend URL.
2.  It should load. If the DB is empty, it will show empty tables.
3.  To fill data immediately:
    *   Go to your **Cron Job** dashboard in Render.
    *   Click **Trigger Run Now**.
    *   Wait for the logs to show "[ingest] Finished...".
    *   Refresh your Frontend.
