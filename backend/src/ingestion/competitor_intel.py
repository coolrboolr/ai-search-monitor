from src.core.logging import get_logger

logger = get_logger(__name__)

async def pull_competitor_clients(company_name: str):
    """
    v0 behavior: log whenever we detect or update a competitor.
    Future versions may enrich this with news, client lists, etc.
    """
    logger.info(f"[intel] Competitor detected or updated: {company_name}")
    return
