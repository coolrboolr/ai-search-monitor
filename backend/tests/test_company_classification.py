import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.ingestion.upsert import upsert_raw_job
from src.ingestion.sources.base import RawJob
from src.db.models import Company, Job
from src.semantic.classifier_company import CompanyClassifier

# Unit test for Classifier
# Unit test for Classifier
def test_company_classifier_logic():
    classifier = CompanyClassifier()
    
    # Heuristic Checks
    assert classifier.classify("Acme SEO Agency") == "Competitor"
    assert classifier.classify("Best SEO Consulting") == "Competitor"
    
    # Strong Client Keywords (override potential ambiguity)
    assert classifier.classify("SaaS Product Platform") == "Client"
    assert classifier.classify("FutureCorp AI", "Leading AI platform for enterprise data.") == "Client"
    
    # Known Ambiguous / Client-leaning
    assert classifier.classify("OpenAI") == "Client"
    assert classifier.classify("Skrapp.io") == "Client"
    
    # Margin / Default Behavior check
    # Something that sounds a bit generic but lacks strong agency keywords should default to Client
    assert classifier.classify("Tech Solutions Inc") == "Client"

    # Explicit Competitor descriptions
    assert classifier.classify("Mannix Marketing", "We are a full-service digital marketing agency.") == "Competitor"

# Integration test for Upsert logic (mocked DB)
@pytest.mark.asyncio
async def test_upsert_creates_competitor_and_triggers_intel():
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    # Setup the result of await session.execute(...)
    mock_result = MagicMock()
    # Setup scalars().first() behavior
    mock_result.scalars.return_value.first.side_effect = [None, None]
    
    # Configure mock_session.execute to return the mock_result when awaited
    mock_session.execute.return_value = mock_result
    
    raw_job = RawJob(
        company="Competitor Agency",
        title="SEO Manager",
        location="Remote",
        url="http://example.com",
        source="linkedin",
        description="We are a leading digital agency.",
        external_id="123"
    )
    
    # Patch the intel pull function
    with patch("src.ingestion.upsert.pull_competitor_clients", new_callable=AsyncMock) as mock_pull:
        await upsert_raw_job(mock_session, raw_job)
        
        # Verify Company was added
        args_list = mock_session.add.call_args_list
        found_company = False
        for args, _ in args_list:
            obj = args[0]
            if isinstance(obj, Company):
                found_company = True
                assert obj.name == "Competitor Agency"
                assert obj.classification == "Competitor"
        
        assert found_company
        
        # Verify Intel Pull Triggered
        mock_pull.assert_called_with("Competitor Agency")

@pytest.mark.asyncio
async def test_upsert_client_company():
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.side_effect = [None, None]
    mock_session.execute.return_value = mock_result
    
    raw_job = RawJob(
        company="Regular Client Inc",
        title="Software Engineer",
        location="Remote",
        url="http://example.com/2",
        source="linkedin",
        description="We sell widgets.",
        external_id="456"
    )
    
    with patch("src.ingestion.upsert.pull_competitor_clients", new_callable=AsyncMock) as mock_pull:
        await upsert_raw_job(mock_session, raw_job)
        
        # Verify Company classification
        args_list = mock_session.add.call_args_list
        found_company = False
        for args, _ in args_list:
            obj = args[0]
            if isinstance(obj, Company):
                found_company = True
                assert obj.classification == "Client"
        
        assert found_company
        
        # Verify Intel Pull NOT Triggered
        mock_pull.assert_not_called()
