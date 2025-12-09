import asyncio
from sqlalchemy import select
from src.db.session import get_session, AsyncSessionLocal
from src.db.models import Job

async def check_data():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(
                Job.title, 
                Job.remote_flag, 
                Job.employment_type, 
                Job.seniority, 
                Job.opp_athena_view,
                Job.opp_confidence
            ).limit(5)
        )
        jobs = result.all()
        print(f"Found {len(jobs)} jobs. Samples:")
        for j in jobs:
            print(f"- {j.title}: Remote={j.remote_flag}, Type={j.employment_type}, Seniority={j.seniority} | Opp={j.opp_athena_view} ({j.opp_confidence})")

if __name__ == "__main__":
    asyncio.run(check_data())
