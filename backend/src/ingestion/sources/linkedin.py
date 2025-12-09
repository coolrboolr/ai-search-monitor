from playwright.async_api import async_playwright
from .base import Source, RawJob
from src.core.config import settings
from src.ingestion.enrich import enrich_raw_job
from src.core.logging import get_logger
import asyncio
import random

logger = get_logger(__name__)

def random_user_agent() -> str:
    # v0: fixed, realistic UA string; randomness not needed yet
    return (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    )

class LinkedInSource(Source):
    """
    Experimental source (not used in v0).
    """
    name = "linkedin"

    async def fetch(self):
        try:
            async with async_playwright() as p:
                # Launch browser (headless=True for prod/testing)
                try:
                    browser = await p.chromium.launch(headless=True)
                except Exception as e:
                    logger.warning("Playwright/Chromium not available, skipping LinkedIn", extra={"source": self.name, "error": str(e)})
                    return

                context = await browser.new_context(
                    user_agent=random_user_agent(),
                    viewport={"width": 1280, "height": 720}
                )
                
                try:
                    # Phase 1: Search & Collect Meta
                    page = await context.new_page()
                    logger.info("Navigating to LinkedIn search...", extra={"source": self.name})
                    
                    # Use a catch-all for Phase 1
                    jobs_to_scrape = []
                    try:
                        await page.goto("https://www.linkedin.com/jobs/search/?keywords=AI%20SEO&location=United%20States", timeout=30000)
                        
                        try:
                            await page.wait_for_selector(".jobs-search__results-list li, .base-card", timeout=10000)
                        except:
                            logger.warning("Timeout waiting for job list", extra={"source": self.name})
                        
                        # Scroll to load more
                        for _ in range(3):
                            await page.mouse.wheel(0, 500)
                            await page.wait_for_timeout(1000)

                        job_cards = await page.locator("div.base-card").all()
                        logger.info(f"Found {len(job_cards)} job cards", extra={"source": self.name})
                        
                        for card in job_cards:
                            try:
                                title_el = card.locator(".base-search-card__title")
                                company_el = card.locator(".base-search-card__subtitle")
                                location_el = card.locator(".job-search-card__location")
                                link_el = card.locator(".base-card__full-link")
                                
                                title = await title_el.inner_text() if await title_el.count() > 0 else "Unknown Title"
                                company = await company_el.inner_text() if await company_el.count() > 0 else "Unknown Company"
                                location = await location_el.inner_text() if await location_el.count() > 0 else "Unknown Location"
                                
                                url = ""
                                if await link_el.count() > 0:
                                    url = await link_el.get_attribute("href")
                                    if url and "?" in url:
                                        url = url.split("?")[0]
                                
                                if url:
                                    jobs_to_scrape.append({
                                        "title": title.strip(),
                                        "company": company.strip(),
                                        "location": location.strip(),
                                        "url": url
                                    })
                            except Exception as e:
                                logger.warning("Error parsing card", extra={"source": self.name, "error": str(e)})
                                continue

                    except Exception as e:
                        logger.warning("Phase 1 failed", extra={"source": self.name, "error": str(e)})
                    finally:
                        # Close the list page as we don't need it for Phase 2
                        await page.close()

                    # Phase 2: Concurrent Detail Fetch using Context
                    sem = asyncio.Semaphore(settings.INGEST_MAX_DETAIL_CONCURRENCY_LINKEDIN)
                    logger.info("Starting detail fetch", extra={"source": self.name, "count": len(jobs_to_scrape), "concurrency": settings.INGEST_MAX_DETAIL_CONCURRENCY_LINKEDIN})

                    async def worker(meta):
                        async with sem:
                            description = None
                            try:
                                # Create new page for this task within the same context
                                detail_page = await context.new_page()
                                # Be polite before loading
                                await asyncio.sleep(random.uniform(1.0, 2.5))
                                
                                try:
                                    await detail_page.goto(meta['url'], timeout=15000)
                                    selector = ".show-more-less-html__markup"
                                    try:
                                        await detail_page.wait_for_selector(selector, timeout=5000)
                                        description_el = detail_page.locator(selector)
                                        if await description_el.count() > 0:
                                            description = await description_el.inner_text()
                                    except Exception:
                                        # Fallback or just ignore
                                        pass
                                finally:
                                    await detail_page.close()
                                    
                            except Exception as e:
                                logger.warning(f"Detail fetch failed for {meta['url']}", extra={"source": self.name, "error": str(e)})

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
                            raw_job = enrich_raw_job(raw_job)
                            return raw_job

                    tasks = [worker(j) for j in jobs_to_scrape]
                    for future in asyncio.as_completed(tasks):
                        try:
                            result = await future
                            yield result
                        except Exception as e:
                             logger.error("Worker exception", extra={"source": self.name, "error": str(e)})

                except Exception as e:
                    logger.error("Error in source", extra={"source": self.name, "error": str(e)})
                finally:
                    await browser.close()
        except Exception as e:
             logger.error("Critical source error", extra={"source": self.name, "error": str(e)})

