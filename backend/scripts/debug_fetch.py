import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.ingestion.sources.seojobs import SEOJobsSource

async def main():
    source = SEOJobsSource()
    print(f"Fetching from {source.name}...")
    count = 0
    async for job in source.fetch():
        desc_preview = (job.description or "")[:50].replace("\n", " ")
        print(f"Got job: {job.title} | {job.company} | Desc len: {len(job.description or '')} | Snippet: {desc_preview}...")
        # Dump one node HTML for inspection (from the source logic, I need to modify the source? 
        # No, I can't access the node here easily because fetch yields RawJob. 
        # I have to modify `seojobs.py` to print the node HTML temporarily.
        count += 1
        if count >= 5:
            break
    print(f"Total fetched (capped at 5): {count}")

if __name__ == "__main__":
    asyncio.run(main())
