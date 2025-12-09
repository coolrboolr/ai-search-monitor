from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.db.session import get_session
from src.db.models import Company, Job
from src.semantic.schema import CompanyOut, JobOut

router = APIRouter()

@router.get("/", response_model=list[CompanyOut])
async def list_companies(
    min_roles: int = Query(1, description="Minimum number of AI Search roles"),
    category: str | None = Query(None),
    region: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
):
    # Group companies by AI-search jobs and aggregate titles
    stmt = (
        select(
            Company,
            func.count(Job.id).label("job_count"),
            func.array_agg(Job.title).label("titles"),
        )
        .join(Job, Job.company_id == Company.id)
        .where(Job.is_ai_search == True)
        .group_by(Company.id)
    )

    if category:
        stmt = stmt.where(Company.category == category)
    if region:
        stmt = stmt.where(Company.region == region)

    stmt = stmt.having(func.count(Job.id) >= min_roles)

    result = await session.execute(stmt)
    rows = result.all()

    outputs: list[Company] = []
    for company, job_count, titles in rows:
        # Attach derived fields for Pydantic
        company.ai_search_roles = job_count
        if titles:
            # Deduplicate while preserving order and keep top 3
            unique_titles = list(dict.fromkeys(titles))
            company.sample_titles = ", ".join(unique_titles[:3])
        else:
            company.sample_titles = None
        outputs.append(company)

    return outputs

@router.get("/{id}/jobs", response_model=list[JobOut])
async def list_company_jobs(
    id: int,
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(Job, Company.name)
        .join(Company, Job.company_id == Company.id)
        .where(Job.company_id == id)
        .where(Job.is_ai_search == True)
        .order_by(Job.posted_at.desc().nullslast())
    )
    result = await session.execute(stmt)
    rows = result.all()

    outputs: list[JobOut] = []
    for job, company_name in rows:
        job.company_name = company_name
        jo = JobOut.model_validate(job, from_attributes=True)
        outputs.append(jo)

    return outputs
