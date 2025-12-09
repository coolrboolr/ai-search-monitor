import asyncio
import sys
import os
from sqlalchemy import select

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.db.session import AsyncSessionLocal
from src.db.models import Job

async def main():
    async with AsyncSessionLocal() as session:
        # Find jobs with None or empty description
        stmt = select(Job).where((Job.description == None) | (Job.description == ""))
        result = await session.execute(stmt)
        jobs = result.scalars().all()
        
        print(f"Total jobs missing description: {len(jobs)}")
        
        if len(jobs) > 0:
            print("Listing first 10:")
            for j in jobs[:10]:
                print(f"- ID: {j.id} | Title: {j.title} | Source: {j.source}")
        else:
            print("Success! All jobs have descriptions.")

        # Also print stats on description length
        stmt_all = select(Job)
        res_all = await session.execute(stmt_all)
        all_jobs = res_all.scalars().all()
        print(f"Total jobs in DB: {len(all_jobs)}")
        if all_jobs:
            avg_len = sum(len(j.description or "") for j in all_jobs) / len(all_jobs)
            print(f"Average description length: {avg_len:.0f} chars")

if __name__ == "__main__":
    asyncio.run(main())
