from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from dateutil import parser
import hashlib


from src.db.models import Job, Company
from src.ingestion.sources.base import RawJob

def generate_dedupe_key(company: str, title: str, location: str | None) -> str:
    raw = f"{company.lower()}|{title.lower()}|{(location or '').lower()}"
    return hashlib.sha256(raw.encode()).hexdigest()

from src.semantic.classifier import classifier
from src.semantic.classifier_company import company_classifier
from src.semantic.opportunity_classifier import classify_opportunity_async
from src.ingestion.competitor_intel import pull_competitor_clients

def normalize_company_name(name: str) -> str:
    n = name.strip()
    # Strip common suffixes
    suffixes = [
        " Inc.", " Inc", " LLC", " LLP", ", Inc.", ", LLC", ", LLP",
        " Ltd.", " Ltd", " Limited", ", Limited", " Co.", " Co", " Corporation", " Corp.", " Corp"
    ]
    for s in suffixes:
        if n.endswith(s):
            n = n[: -len(s)]
    return n.strip()

def parse_date_safe(date_str: str | None) -> datetime:
    if not date_str:
        return datetime.utcnow()
    try:
        return parser.parse(date_str)
    except Exception:
        return datetime.utcnow()

async def upsert_raw_job(session: AsyncSession, raw_job: RawJob):
    # 1. Get or Create Company
    company_name_raw = raw_job.company or ""
    company_name = normalize_company_name(company_name_raw)
    result = await session.execute(select(Company).where(Company.name == company_name))
    company = result.scalars().first()
    
    # Classify company
    # OpenAI-backed opportunity classification (AthenaHQ view) - Async
    opp = await classify_opportunity_async(company_name, raw_job.title, raw_job.description)
    
    # Semantic classifier fallback
    semantic_classification = company_classifier.classify(company_name, raw_job.description)
    
    # Decide final classification
    if opp and opp.confidence >= 0.6:
        classification = "Client" if opp.athena_view == "Client" else (
            "Competitor" if opp.athena_view == "Competitor" else semantic_classification
        )
    else:
        classification = semantic_classification

    # Append OpenAI metadata to description (in-memory only for upsert)
    # Also populate Job fields later
    if opp:
        meta_line = (
            f"OPP_META: athena_view={opp.athena_view}; "
            f"role_type={opp.company_role_type}; "
            f"buyer_or_seller={opp.buyer_or_seller}; "
            f"confidence={opp.confidence:.2f}"
        )
        existing_desc = raw_job.description or ""
        if "OPP_META:" not in existing_desc:
            raw_job.description = f"{meta_line} || {existing_desc}".strip()
    
    from sqlalchemy.exc import IntegrityError
    
    if not company:
        company = Company(
            name=company_name, 
            classification=classification,
            industry=opp.industry if opp else None,
        )
        # v0: simple heuristic so UI has a useful category
        if classification == "Competitor":
            company.category = "Agency / Consultancy"
        else:
            company.category = "SaaS / Tools"
        session.add(company)
        try:
            await session.flush()
        except IntegrityError:
            await session.rollback()
            # Race condition: Company created by another worker
            result = await session.execute(select(Company).where(Company.name == company_name))
            company = result.scalars().first()
    else:
        if not company.classification:
            company.classification = classification
        if opp and opp.industry and not company.industry:
            company.industry = opp.industry
        if not company.category:
            company.category = "Agency / Consultancy" if company.classification == "Competitor" else "SaaS / Tools"
    
    # Trigger Competitor Intel Pull
    if company.classification == "Competitor":
        await pull_competitor_clients(company.name)
    
    # 2. Dedupe Key
    dedupe_key = generate_dedupe_key(company_name, raw_job.title, raw_job.location)
    
    # 3. Check existing job
    result = await session.execute(select(Job).where(Job.dedupe_key == dedupe_key))
    existing_job = result.scalars().first()
    
    # Calculate scores (reuse cache if available)
    relevance_score = raw_job.meta_score if raw_job.meta_score is not None else classifier.score(raw_job.title, raw_job.description)
    role_tier = classifier.tier(raw_job.title, raw_job.description)
    is_ai_search = role_tier != "out_of_scope"
    
    # Basic job fields that might update
    update_data = {
        "scraped_at": datetime.utcnow(),
        "relevance_score": relevance_score,
        "is_ai_search": is_ai_search,
        "role_tier": role_tier,
        "remote_flag": raw_job.remote_flag,
        "employment_type": raw_job.employment_type,
        "seniority": raw_job.seniority,
        "ai_forward": raw_job.ai_forward,
        
        # Opportunity fields if available
        "opp_athena_view": opp.athena_view if opp else None,
        "opp_role_type": opp.company_role_type if opp else None,
        "opp_buyer_or_seller": opp.buyer_or_seller if opp else None,
        "opp_confidence": opp.confidence if opp else None,
    }

    if existing_job:
        # Update
        existing_job.scraped_at = update_data["scraped_at"]
        existing_job.relevance_score = update_data["relevance_score"]
        existing_job.is_ai_search = update_data["is_ai_search"]
        existing_job.role_tier = update_data["role_tier"]
        
        # Update metadata if present
        existing_job.remote_flag = update_data["remote_flag"]
        existing_job.employment_type = update_data["employment_type"]
        existing_job.seniority = update_data["seniority"]
        existing_job.ai_forward = update_data["ai_forward"]
        
        if opp:
            existing_job.opp_athena_view = update_data["opp_athena_view"]
            existing_job.opp_role_type = update_data["opp_role_type"]
            existing_job.opp_buyer_or_seller = update_data["opp_buyer_or_seller"]
            existing_job.opp_confidence = update_data["opp_confidence"]

        if raw_job.description:
            if not existing_job.description or existing_job.description != raw_job.description:
                existing_job.description = raw_job.description
                
    else:
        # Insert
        new_job = Job(
            company_id=company.id,
            dedupe_key=dedupe_key,
            external_id=raw_job.external_id,
            source=raw_job.source,
            title=raw_job.title,
            location=raw_job.location,
            url=raw_job.url,
            description=raw_job.description,
            posted_at=parse_date_safe(raw_job.posted_at),

            relevance_score=relevance_score,
            is_ai_search=is_ai_search,
            role_tier=role_tier,
            
            # New fields
            remote_flag=update_data["remote_flag"],
            employment_type=update_data["employment_type"],
            seniority=update_data["seniority"],
            ai_forward=update_data["ai_forward"],
            
            opp_athena_view=update_data["opp_athena_view"],
            opp_role_type=update_data["opp_role_type"],
            opp_buyer_or_seller=update_data["opp_buyer_or_seller"],
            opp_confidence=update_data["opp_confidence"]
        )
        session.add(new_job)
    
    # Update last_seen whenever we touch this company
    company.last_seen = datetime.utcnow()

    await session.commit()
