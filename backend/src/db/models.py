from sqlalchemy import (
    String, Integer, Boolean, DateTime, ForeignKey, Float, Text
)
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from datetime import datetime

Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True, unique=True)
    website: Mapped[str | None] = mapped_column(String, nullable=True)
    careers_url: Mapped[str | None] = mapped_column(String, nullable=True)
    category: Mapped[str | None] = mapped_column(String, nullable=True)  # "SaaS", "Agency", etc.
    region: Mapped[str | None] = mapped_column(String, nullable=True)
    classification: Mapped[str | None] = mapped_column(String, nullable=True, index=True) # "Client", "Competitor"
    
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    jobs = relationship("Job", back_populates="company")

class Job(Base):
    __tablename__ = "jobs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    
    # Deduplication and Tracking
    dedupe_key: Mapped[str] = mapped_column(String, unique=True, index=True) # hash(company+title+loc)
    external_id: Mapped[str | None] = mapped_column(String, nullable=True)
    source: Mapped[str] = mapped_column(String, index=True)
    
    # Core Data
    title: Mapped[str] = mapped_column(String, index=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    url: Mapped[str | None] = mapped_column(String, nullable=True)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    scraped_at: Mapped[datetime] = mapped_column(DateTime, index=True, default=datetime.utcnow)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Semantic / AI Layers
    relevance_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_ai_search: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    # Structured Metadata (v0.1)
    remote_flag: Mapped[str | None] = mapped_column(String, nullable=True)
    employment_type: Mapped[str | None] = mapped_column(String, nullable=True)
    seniority: Mapped[str | None] = mapped_column(String, nullable=True)
    ai_forward: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # Opportunity Metadata (OpenAI)
    opp_athena_view: Mapped[str | None] = mapped_column(String, nullable=True) # Client, Competitor, Neutral
    opp_role_type: Mapped[str | None] = mapped_column(String, nullable=True) # AgencyProvider, BrandBuyer, PlatformSaaS...
    opp_buyer_or_seller: Mapped[str | None] = mapped_column(String, nullable=True) # Buyer, Seller
    opp_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Vector Embedding
    embedding = mapped_column(Vector(384), nullable=True)  # v0: optional

    company = relationship("Company", back_populates="jobs")
