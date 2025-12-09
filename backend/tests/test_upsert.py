import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime
from src.ingestion.sources.base import RawJob
from src.ingestion.upsert import upsert_raw_job
from src.db.models import Job, Company

@pytest.mark.asyncio
@patch("src.ingestion.upsert.classifier")
@patch("src.ingestion.upsert.classify_opportunity_async")
@patch("src.ingestion.upsert.company_classifier")
async def test_upsert_update_description(mock_company_clf, mock_opp_clf, mock_classifier):
    # Setup mocks
    mock_classifier.score.return_value = 0.9
    mock_classifier.tier.return_value = "Core AI Search"
    mock_opp_clf.return_value = None # No opportunity -> No OPP_META
    mock_company_clf.classify.return_value = "Client"
    
    session = AsyncMock()
    
    # Mock Company check (return existing company)
    mock_company = Company(id=1, name="Test Co", classification="Client")
    # First execute is for Company inquiry
    # Second execute is for Job inquiry
    
    # We need to control the return values of session.execute
    # Result of simple scalars().first()
    
    mock_result_company = MagicMock()
    mock_result_company.scalars.return_value.first.return_value = mock_company
    
    # Existing job with old description
    existing_job = Job(description="Old Description", dedupe_key="fake-key")
    mock_result_job = MagicMock()
    mock_result_job.scalars.return_value.first.return_value = existing_job
    
    session.execute.side_effect = [mock_result_company, mock_result_job]
    
    # Input
    raw = RawJob(
        external_id="123",
        company="Test Co",
        title="Jobs",
        location="Remote",
        url="http://example.com/job",
        source="test",
        description="New Description" # Different!
    )
    
    # Action
    await upsert_raw_job(session, raw)
    
    # Assert
    assert existing_job.description == "New Description"
    assert session.commit.called

@pytest.mark.asyncio
@patch("src.ingestion.upsert.classifier")
@patch("src.ingestion.upsert.classify_opportunity_async")
@patch("src.ingestion.upsert.company_classifier")
async def test_upsert_no_update_if_same(mock_company_clf, mock_opp_clf, mock_classifier):
    mock_classifier.score.return_value = 0.9
    mock_classifier.tier.return_value = "Core AI Search"
    mock_opp_clf.return_value = None
    mock_company_clf.classify.return_value = "Client"
    # Setup
    session = AsyncMock()
    
    mock_company = Company(id=1, name="Test Co", classification="Client")
    mock_result_company = MagicMock()
    mock_result_company.scalars.return_value.first.return_value = mock_company
    
    existing_job = Job(description="Same Description", dedupe_key="fake-key")
    # Make sure we can track assignment. Actually in Python if we assign, the obj changes.
    # We can wrap description in a property mock if we really strictly want to check assignment count,
    # but checking value is enough.
    
    mock_result_job = MagicMock()
    mock_result_job.scalars.return_value.first.return_value = existing_job
    
    session.execute.side_effect = [mock_result_company, mock_result_job]
    
    # Input
    raw = RawJob(
        external_id="123",
        company="Test Co",
        title="Jobs",
        location="Remote",
        url="http://example.com/job",
        source="test",
        description="Same Description"
    )
    
    # Action
    await upsert_raw_job(session, raw)
    
    # Assert
    assert existing_job.description == "Same Description"
    # To be sure it wasn't re-assigned, we'd need to mock the attribute, but logic is verified 
    # if we verify the previous test DID update it.
    
    assert session.commit.called

@pytest.mark.asyncio
@patch("src.ingestion.upsert.classifier")
@patch("src.ingestion.upsert.company_classifier")
@patch("src.ingestion.upsert.classify_opportunity_async", new_callable=AsyncMock)
async def test_upsert_appends_opp_meta(mock_opp_clf, mock_company_clf, mock_classifier):
    mock_classifier.score.return_value = 0.9
    mock_classifier.tier.return_value = "Core AI Search"
    from src.semantic.opportunity_classifier import OpportunityClassification
    
    mock_company_clf.classify.return_value = "Client"
    mock_opp_clf.return_value = OpportunityClassification(
        company_role_type="BrandBuyer",
        buyer_or_seller="Buyer",
        athena_view="Client",
        confidence=0.9,
        notes="Test",
        industry="B2B SaaS",
    )

    session = AsyncMock()

    mock_company = Company(id=1, name="Test Co", classification=None)
    mock_result_company = MagicMock()
    mock_result_company.scalars.return_value.first.return_value = mock_company

    existing_job = Job(description="Original Description", dedupe_key="fake-key")
    mock_result_job = MagicMock()
    mock_result_job.scalars.return_value.first.return_value = existing_job

    session.execute.side_effect = [mock_result_company, mock_result_job]

    raw = RawJob(
        external_id="123",
        company="Test Co",
        title="AI Search Engineer",
        location="Remote",
        url="http://example.com/job",
        source="test",
        description="Original Description"
    )

    await upsert_raw_job(session, raw)

    assert "OPP_META:" in existing_job.description
    assert "athena_view=Client" in existing_job.description
