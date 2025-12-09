from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.db.session import get_session
from src.db.models import Company, Job
from src.semantic.schema import StatsOut

router = APIRouter()


@router.get("/", response_model=StatsOut)
async def get_stats(
    session: AsyncSession = Depends(get_session),
):
    # Total companies
    result = await session.execute(select(func.count(Company.id)))
    total_companies = result.scalar_one() or 0

    # Total AI-search jobs
    result = await session.execute(
        select(func.count(Job.id)).where(Job.is_ai_search == True)  # noqa: E712
    )
    total_jobs = result.scalar_one() or 0

    # Competitors
    result = await session.execute(
        select(func.count(Company.id)).where(Company.classification == "Competitor")
    )
    total_competitors = result.scalar_one() or 0

    # Clients
    result = await session.execute(
        select(func.count(Company.id)).where(Company.classification == "Client")
    )
    total_clients = result.scalar_one() or 0

    # Last ingestion (scraped_at max)
    result = await session.execute(select(func.max(Job.scraped_at)))
    last_ingestion_at = result.scalar_one()
    # FastAPI will serialize datetime → ISO 8601; keep None if no jobs yet.

    return StatsOut(
        total_companies=int(total_companies),
        total_jobs=int(total_jobs),
        total_competitors=int(total_competitors),
        total_clients=int(total_clients),
        last_ingestion_at=last_ingestion_at,
    )
