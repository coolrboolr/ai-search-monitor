from pydantic import BaseModel, ConfigDict
from datetime import datetime

class CompanyOut(BaseModel):
    id: int
    name: str
    website: str | None
    industry: str | None = None
    careers_url: str | None
    category: str | None
    region: str | None
    classification: str | None
    last_seen: datetime | None
    ai_search_roles: int = 0
    sample_titles: str | None = None # For UI display

    model_config = ConfigDict(from_attributes=True)

class JobOut(BaseModel):
    id: int
    title: str
    company_name: str | None = None
    location: str | None
    posted_at: datetime | None
    url: str | None
    relevance_score: float | None
    source: str | None = None
    
    is_ai_search: bool = False
    role_tier: str | None = None
    # Structured Metadata
    remote_flag: str | None = None
    employment_type: str | None = None
    seniority: str | None = None
    ai_forward: bool | None = None
    
    # Opportunity Metadata
    opp_athena_view: str | None = None
    opp_role_type: str | None = None
    opp_confidence: float | None = None

    model_config = ConfigDict(from_attributes=True)

class JobDetailOut(BaseModel):
    id: int
    title: str
    company_name: str | None = None
    location: str | None
    posted_at: datetime | None
    url: str | None
    relevance_score: float | None

    # Detail-only fields
    description: str | None
    dedupe_key: str
    company_classification: str | None = None
    company_category: str | None = None
    
    # Re-declare to ensure they are available in detail view too (inherited or explicit)
    remote_flag: str | None = None
    employment_type: str | None = None
    seniority: str | None = None
    ai_forward: bool | None = None
    
    opp_athena_view: str | None = None
    opp_role_type: str | None = None
    opp_buyer_or_seller: str | None = None
    opp_confidence: float | None = None

    model_config = ConfigDict(from_attributes=True)

class StatsOut(BaseModel):
    total_companies: int
    total_jobs: int
    total_competitors: int
    total_clients: int
    last_ingestion_at: datetime | None

    model_config = ConfigDict(from_attributes=True)

