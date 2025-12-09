import httpx
from src.ingestion.enrich import enrich_raw_job
from selectolax.parser import HTMLParser
from .base import Source, RawJob
from src.core.config import settings
from src.core.logging import get_logger
import random
import asyncio
import json
from urllib.parse import urljoin

logger = get_logger(__name__)

def random_headers():
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    ]
    return {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }

class SEOJobsSource(Source):
    name = "seojobs"

    async def fetch(self):
        # Phase 1: List Parsing
        jobs_meta = []
        
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            try:
                resp = await client.get("https://seojobs.com/", headers=random_headers())
                resp.raise_for_status()
                
                html = HTMLParser(resp.text)
                nodes = html.css("div.job-item")
                logger.info(f"Found job items", extra={"source": self.name, "count": len(nodes)})
                
                for node in nodes:
                    try:
                        # Title often contains "Title ~ Company ~ Salary ~ Location"
                        title_node = node.css_first("h3 a")
                        if not title_node:
                            continue
                        
                        full_text = title_node.text(strip=True)
                        parts = [p.strip() for p in full_text.split("~")]
                        
                        # Heuristic parsing
                        title = parts[0] if len(parts) > 0 else "Unknown Title"
                        company = parts[1] if len(parts) > 1 else "Unknown Company"
                        
                        location_node = node.css_first(".job-place")
                        location = location_node.text(strip=True) if location_node else None
                        
                        if not location and len(parts) > 2:
                            location = parts[-1] 

                        # Regularize Location
                        if location:
                            if "remote" in location.lower():
                                location = "Remote"
                            else:
                                loc_parts = [p.strip() for p in location.split(",")]
                                seen = set()
                                deduped = []
                                for p in loc_parts:
                                    if p not in seen:
                                        seen.add(p)
                                        deduped.append(p)
                                location = ", ".join(deduped)

                        raw_link_url = title_node.attributes.get("href", "")
                        link_url = urljoin("https://seojobs.com/", raw_link_url)
                        
                        if link_url:
                            jobs_meta.append({
                                "title": title,
                                "company": company,
                                "location": location,
                                "url": link_url
                            })
                            
                    except Exception as e:
                        logger.warning("Error parsing node", extra={"source": self.name, "error": str(e)})
                        continue
                        
            except httpx.HTTPError as e:
                logger.error("Error fetching list", extra={"source": self.name, "error": str(e)})
                return

        # Phase 2: Concurrent Detail Fetch
        sem = asyncio.Semaphore(settings.INGEST_MAX_DETAIL_CONCURRENCY_SEO)
        logger.info(f"Starting detail fetch", extra={"source": self.name, "count": len(jobs_meta), "concurrency": settings.INGEST_MAX_DETAIL_CONCURRENCY_SEO})

        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as detail_client:
            async def worker(meta):
                async with sem:
                    description = ""
                    retries = 3
                    
                    # Fetch detailed description from the job page
                    for attempt in range(retries):
                        try:
                            # Sleep briefly to be polite even inside semaphore
                            await asyncio.sleep(random.uniform(0.5, 1.5))
                            
                            detail_resp = await detail_client.get(meta['url'], headers=random_headers())
                            if detail_resp.status_code == 200:
                                detail_html = HTMLParser(detail_resp.text)
                                # JSON-LD Check
                                scripts = detail_html.css('script[type="application/ld+json"]')
                                found_json_desc = False
                                for s in scripts:
                                    try:
                                        data = json.loads(s.text())
                                        graph = data.get("@graph", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
                                        if not graph and isinstance(data, dict):
                                                graph = [data]
                                        for item in graph:
                                            if item.get("@type") == "JobPosting":
                                                description = item.get("description", "")
                                                found_json_desc = True
                                                break
                                        if found_json_desc:
                                            break
                                    except:
                                        continue
                                
                                # DOM Fallback
                                if not description:
                                    content_node = detail_html.css_first(".entry-content, .job-description, .single-job")
                                    if content_node:
                                        description = content_node.text(strip=True)
                                
                                # Success
                                break
                            elif detail_resp.status_code >= 500:
                                # Retryable
                                if attempt < retries - 1:
                                    await asyncio.sleep(1 * (attempt + 1))
                                    continue
                            else:
                                # 4xx, etc.
                                break
                        except Exception as err:
                            if attempt < retries - 1:
                                await asyncio.sleep(1 * (attempt + 1))
                                continue
                            logger.warning(f"Failed to fetch details", extra={"source": self.name, "url": meta['url'], "error": str(err)})

                    raw_job = RawJob(
                        external_id=meta['url'],
                        title=meta['title'],
                        company=meta['company'],
                        location=meta['location'],
                        url=meta['url'],
                        source=self.name,
                        posted_at=None,
                        description=description 
                    )
                    
                    # Enrich (populates metadata fields)
                    raw_job = enrich_raw_job(raw_job)
                    return raw_job

            # Use as_completed to yield results as they come in
            tasks = [worker(m) for m in jobs_meta]
            for future in asyncio.as_completed(tasks):
                try:
                    result = await future
                    if result:
                        yield result
                except Exception as e:
                    logger.error("Worker exception", extra={"source": self.name, "error": str(e)})

