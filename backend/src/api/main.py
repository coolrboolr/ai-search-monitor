from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import companies, jobs, stats
from src.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Updated prefixes for v0
app.include_router(companies.router, prefix="/api/companies", tags=["companies"])
app.include_router(jobs.router,     prefix="/api/jobs",       tags=["jobs"])
app.include_router(stats.router,   prefix="/api/stats",      tags=["stats"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
