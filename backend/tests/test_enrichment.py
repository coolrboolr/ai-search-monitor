import pytest
from src.ingestion.sources.base import RawJob
from src.ingestion.enrich import enrich_raw_job

def test_enrich_preserves_description():
    raw = RawJob(
        external_id="123",
        company="Test Co",
        title="Remote (USA) AI Engineer",
        location="Remote",
        url="http://example.com",
        source="test",
        description="Original valuable content."
    )
    enriched = enrich_raw_job(raw)
    
    # Check that original text is still there
    assert "Original valuable content." in enriched.description
    
    # Check that META was added (assuming inference triggers it, e.g. remote or title)
    # "Remote" location -> META: remote=remote
    assert "META:" in enriched.description
    assert "remote=remote" in enriched.description
    
    # Verify structure
    parts = enriched.description.split(" || ")
    assert len(parts) >= 2
    assert parts[-1] == "Original valuable content."

def test_enrich_with_empty_description():
    raw = RawJob(
        external_id="124",
        company="Test Co",
        title="Senior AI Engineer", # Seniority inference
        location="Onsite",
        url="http://example.com",
        source="test",
        description=""
    )
    enriched = enrich_raw_job(raw)
    
    assert "META:" in enriched.description
    assert "seniority=senior" in enriched.description
    # Should end with || (empty string)
    assert enriched.description.endswith("||")

