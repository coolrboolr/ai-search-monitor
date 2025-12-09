import asyncio
from src.db.session import AsyncSessionLocal
from src.ingestion.sources.seojobs import SEOJobsSource
from src.ingestion.sources.linkedin import LinkedInSource
from src.ingestion.upsert import upsert_raw_job
from src.semantic.classifier import classifier
from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

async def process_job_safe(job, upsert_sem, stats):
    """
    Worker to upsert a job with its own DB session, bounded by semaphore.
    """
    async with upsert_sem:
        try:
            # Re-check relevance mainly for stats (or if source didn't filter heavily)
            # We already filter below, but good to be consistent
            async with AsyncSessionLocal() as session:
                await upsert_raw_job(session, job)
            stats['upserted'] += 1
        except Exception as e:
            print(f"Error upserting job {job.url}: {e}")
            stats['errors'] += 1

async def run_ingestion():
    """
    v0.1 Hardened Ingestion:
    - Parallel fetch from SEOJobs + LinkedIn
    - Bounded concurrency for upserts
    - Shared stats
    """
    sources = [
        SEOJobsSource(),
    ]

    if settings.ENABLE_LINKEDIN:
        sources.append(LinkedInSource())
    
    # Shared concurrency gate for DB writes
    upsert_sem = asyncio.Semaphore(settings.INGEST_MAX_UPSERT_CONCURRENCY)
    
    for source in sources:
        logger.info("Starting source", extra={"source": source.name})
        
        stats = {
            'seen': 0,
            'relevant': 0,
            'skipped': 0,
            'upserted': 0,
            'errors': 0
        }
        
        tasks = []
        
        try:
            async for job in source.fetch():
                stats['seen'] += 1
                
                # Pre-filter for relevance to save DB/LLM cycles
                # Cache the score so upsert logic doesn't re-embed
                score = classifier.score(job.title, job.description)
                job.meta_score = score

                if classifier.is_relevant(job.title, job.description):
                    stats['relevant'] += 1
                    # Schedule upsert
                    t = asyncio.create_task(process_job_safe(job, upsert_sem, stats))
                    tasks.append(t)
                else:
                    stats['skipped'] += 1
                    
            # Wait for all upserts for this source to finish
            if tasks:
                logger.info(f"Waiting for {len(tasks)} upsert tasks...", extra={"source": source.name})
                await asyncio.gather(*tasks)
            
            logger.info(f"Finished {source.name}", extra={"stats": stats})
            
        except Exception as e:
            logger.error(f"Critical error running source {source.name}", extra={"error": str(e)})

if __name__ == "__main__":
    asyncio.run(run_ingestion())
