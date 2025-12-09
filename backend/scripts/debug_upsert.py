print("Starting debug script...", flush=True)
import asyncio
import sys
import os

print("Imports started...", flush=True)
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.db.session import AsyncSessionLocal
    print("Imported Session", flush=True)
    from src.ingestion.sources.base import RawJob
    print("Imported RawJob", flush=True)
    from src.ingestion.upsert import upsert_raw_job
    print("Imported upsert_raw_job", flush=True)
    from src.ingestion.enrich import enrich_raw_job
    print("Imported enrich", flush=True)
    from sqlalchemy import select
    from src.db.models import Job
except Exception as e:
    print(f"Import error: {e}", flush=True)
    sys.exit(1)

print("Imports done.", flush=True)

async def main():
    print("Testing upsert...", flush=True)
    job = RawJob(
        external_id="test-job-123",
        title="Test AI Job",
        company="Test Company Inc.",
        location="Remote",
        url="http://example.com",
        source="test",
        description="We are looking for an AI engineer."
    )
    job = enrich_raw_job(job)
    
    try:
        async with AsyncSessionLocal() as session:
            await upsert_raw_job(session, job)
            
            # Verify
            result = await session.execute(select(Job).where(Job.external_id == "test-job-123"))
            db_job = result.scalars().first()
            if db_job:
                print(f"Success! Job inserted with ID {db_job.id}", flush=True)
                print(f"Meta: {db_job.description[:50]}...", flush=True)
            else:
                print("Failed! Job not found.", flush=True)
    except Exception as e:
        print(f"Upsert error: {e}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
