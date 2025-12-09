from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.db.session import get_session
from src.db.models import Job, Company
from src.semantic.schema import JobOut, JobDetailOut

router = APIRouter()

from sqlalchemy.orm import selectinload

@router.get("/", response_model=list[JobOut])
async def list_jobs(
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(Job)
        .options(selectinload(Job.company))
        .join(Job.company)
        .where(Job.is_ai_search == True)
        .order_by(Job.posted_at.desc().nullslast())
        .limit(limit)
    )
    result = await session.execute(stmt)
    jobs = result.scalars().all()

    outputs: list[JobOut] = []
    for job in jobs:
        # Pydantic needs company_name to be present
        job.company_name = job.company.name
        jo = JobOut.model_validate(job, from_attributes=True)
        outputs.append(jo)

    return outputs

@router.get("/{id}", response_model=JobDetailOut)
async def get_job(
    id: int,
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(Job, Company)
        .join(Job.company)
        .where(Job.id == id)
    )
    result = await session.execute(stmt)
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")

    job, company = row

    # Inject view fields used by Pydantic
    job.company_name = company.name
    return JobDetailOut(
        id=job.id,
        title=job.title,
        company_name=job.company_name,
        location=job.location,
        posted_at=job.posted_at,
        url=job.url,
        relevance_score=job.relevance_score,
        description=job.description,
        dedupe_key=job.dedupe_key,
        company_classification=company.classification,
        company_category=company.category,
    )
