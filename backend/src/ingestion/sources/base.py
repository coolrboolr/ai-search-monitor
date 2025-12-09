from typing import Iterable, AsyncGenerator
from pydantic import BaseModel
from datetime import datetime

class RawJob(BaseModel):
    external_id: str | None
    title: str
    company: str
    location: str | None
    url: str
    source: str
    posted_at: str | None = None
    description: str | None = None
    
    # Optional metadata
    raw_data: dict | None = None
    meta_score: float | None = None

    # Enriched Metadata
    remote_flag: str | None = None
    employment_type: str | None = None
    seniority: str | None = None
    ai_forward: bool | None = None

class Source:
    name: str

    async def fetch(self) -> AsyncGenerator[RawJob, None]:
        """
        Yields RawJob objects.
        """
        raise NotImplementedError
