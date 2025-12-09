import asyncio
import sys
import os
from sqlalchemy import select

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.db.session import AsyncSessionLocal
from src.db.models import Job

async def inspect():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Job).limit(5))
        jobs = result.scalars().all()
        print(f"Found {len(jobs)} jobs. Checking for OPP_META...")
        for job in jobs:
            if "OPP_META" in (job.description or ""):
                print(f"MATCH [Job {job.id}]: {job.description[:150]}...")
            else:
                print(f"NO MATCH [Job {job.id}]: {job.description[:50]}...")

if __name__ == "__main__":
    asyncio.run(inspect())
