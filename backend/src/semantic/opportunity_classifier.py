import os
from dataclasses import dataclass
from typing import Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

from openai import OpenAI
from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

OPENAI_OPP_MODEL = settings.OPENAI_OPP_MODEL

# Global Concurrency Control
_OPP_SEM = asyncio.Semaphore(settings.OPENAI_OPP_MAX_CONCURRENCY)
_OPP_CACHE = {} # Key: company_name.lower().strip() -> OpportunityClassification | None

@dataclass
class OpportunityClassification:
    company_role_type: str         # "AgencyProvider", "BrandBuyer", "PlatformSaaS", "Recruiter", "Other"
    buyer_or_seller: str           # "Buyer", "Seller", "Unknown"
    athena_view: str               # "Client", "Competitor", "Neutral"
    confidence: float              # 0–1
    notes: str                     # short rationale
    industry: str | None = None    # "B2B SaaS", "SEO Agency", etc.

def _get_client() -> Optional[OpenAI]:
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        logger.info("[opp_class] OPENAI_API_KEY not set; skipping OpenAI classification")
        return None
    return OpenAI(api_key=api_key)

def classify_opportunity(
    company_name: str,
    title: str,
    description: Optional[str] = None,
) -> Optional[OpportunityClassification]:
    """
    Sync implementation. Kept for reference or direct usage.
    """
    client = _get_client()
    if client is None:
        return None

    text = f"Company: {company_name}\nTitle: {title}\nDescription: {description or ''}"

    system_msg = (
        "You are an analyst for AthenaHQ, a company that SELLS AI search and AEO services.\n"
        "Your job is to classify job postings into:\n"
        "  company_role_type: one of [AgencyProvider, BrandBuyer, PlatformSaaS, Recruiter, Other]\n"
        "  buyer_or_seller: one of [Buyer, Seller, Unknown]\n"
        "  athena_view: one of [Client, Competitor, Neutral]\n"
        "  industry: a concise industry label like 'B2B SaaS', 'SEO Agency', "
        "'Consumer Marketplace', 'Cloud Infrastructure', 'Media & Publishing', etc.\n\n"
        "Guidance:\n"
        "- Agencies, consultancies, and SEO firms that provide services to multiple clients are usually SELLERS -> Competitors.\n"
        "- Brands, SaaS products, or end-companies hiring SEO / AI search people for their own product or marketing are BUYERS -> Clients.\n"
        "- Recruiters and staffing firms are usually Neutral unless they clearly own the SEO delivery.\n"
        "- When ambiguous, lean toward Client (we care more about not missing potential buyers).\n"
        "- Always justify your labels in 'notes'.\n"
        "- Answer in strict JSON with exactly these keys: "
        "company_role_type, buyer_or_seller, athena_view, confidence, notes, industry."
    )

    user_msg = f"Analyze this job posting and classify it:\n\n{text}"

    try:
        resp = client.chat.completions.create(
            model=OPENAI_OPP_MODEL,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.0,
        )
        raw = resp.choices[0].message.content or "{}"

        # cleanup code blocks if any
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()

        import json
        data = json.loads(raw)

        # Robust confidence parsing
        raw_conf = data.get("confidence", 0.5)
        try:
            confidence = float(raw_conf)
        except (ValueError, TypeError):
            if isinstance(raw_conf, str):
                s = raw_conf.lower()
                if "high" in s: confidence = 0.9
                elif "medium" in s: confidence = 0.6
                elif "low" in s: confidence = 0.3
                else: confidence = 0.5
            else:
                confidence = 0.5

        industry = data.get("industry")
        return OpportunityClassification(
            company_role_type=str(data.get("company_role_type", "Other")),
            buyer_or_seller=str(data.get("buyer_or_seller", "Unknown")),
            athena_view=str(data.get("athena_view", "Neutral")),
            confidence=confidence,
            notes=str(data.get("notes", "")),
            industry=str(industry) if industry else None,
        )
    except Exception as e:
        logger.warning(f"[opp_class] OpenAI classification failed: {e}")
        return None

async def classify_opportunity_async(
    company_name: str,
    title: str,
    description: Optional[str] = None
) -> Optional[OpportunityClassification]:
    """
    Async wrapper with caching and concurrency control.
    """
    cache_key = company_name.lower().strip()
    if cache_key in _OPP_CACHE:
        return _OPP_CACHE[cache_key]

    async with _OPP_SEM:
        # Run sync OpenAI call in thread pool to avoid blocking event loop
        loop = asyncio.get_running_loop()
        try:
            result = await loop.run_in_executor(
                None, 
                classify_opportunity, 
                company_name, 
                title, 
                description
            )
            # Cache the result (even if None, to avoid retrying failures repeatedly? 
            # Ideally cache successful ones. If None, we might want to retry next time?
            # Let's cache success only for now.)
            if result:
                _OPP_CACHE[cache_key] = result
            return result
        except Exception as e:
            logger.error(f"[opp_class] Async wrapper error: {e}")
            return None
