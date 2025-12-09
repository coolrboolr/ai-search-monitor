import pytest
import datetime
from unittest.mock import MagicMock

from src.db.models import Company, Job

@pytest.mark.asyncio
async def test_health_check(app_client):
    async with app_client as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_list_companies(app_client, mock_session):
    mock_result = MagicMock()
    company = Company(id=1, name="Test Company", category="SaaS / Tools")
    
    # Mock aggregation row: (Company, job_count, titles_list)
    mock_result.all.return_value = [
        (company, 3, ["AI SEO Specialist", "Search Engineer", "SEO Manager"])
    ]
    mock_session.execute.return_value = mock_result
    
    async with app_client as client:
        resp = await client.get("/api/companies/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1

        row = data[0]
        assert row["name"] == "Test Company"
        assert row["ai_search_roles"] == 3
        assert isinstance(row["sample_titles"], str)
        # Ensure at least one of the mocked titles is present
        assert "AI SEO Specialist" in row["sample_titles"]

@pytest.mark.asyncio
async def test_list_jobs(app_client, mock_session):
    job = Job(
        id=1,
        company_id=1,
        dedupe_key="dk",
        external_id="ext-1",
        source="seo_jobs",
        title="AI SEO Specialist",
        location="Remote",
        url="https://example.com/job1",
        posted_at=None,
        scraped_at=None,
        description="",
        relevance_score=0.9,
        is_ai_search=True,
    )
    job.company = Company(id=1, name="Test Company")

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [job]
    mock_session.execute.return_value = mock_result

    async with app_client as client:
        resp = await client.get("/api/jobs/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        row = data[0]
        assert row["title"] == "AI SEO Specialist"
        assert row["company_name"] == "Test Company"
        assert row["relevance_score"] == 0.9
        assert row["location"] == "Remote"
        assert row["url"] == "https://example.com/job1"
        assert row["posted_at"] is None
@pytest.mark.asyncio
async def test_job_detail(app_client, mock_session):
    company = Company(id=1, name="Test Company", classification="Client", category="SaaS / Tools")
    job = Job(
        id=1,
        company_id=1,
        dedupe_key="abc123",
        external_id="ext-1",
        source="seo_jobs",
        title="AI SEO Specialist",
        location="Remote",
        url="https://example.com/job1",
        posted_at=None,
        scraped_at=None,
        description="META: ai_forward=true || OPP_META: athena_view=Client; ...",
        relevance_score=0.9,
        is_ai_search=True,
    )
    job.company = company

    mock_result = MagicMock()
    mock_result.first.return_value = (job, company)
    mock_session.execute.return_value = mock_result

    async with app_client as client:
        resp = await client.get("/api/jobs/1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == 1
        assert data["title"] == "AI SEO Specialist"
        assert data["company_name"] == "Test Company"
        assert data["company_classification"] == "Client"
        assert data["company_category"] == "SaaS / Tools"
        assert data["dedupe_key"] == "abc123"
        assert "META:" in data["description"]

@pytest.mark.asyncio
async def test_job_detail_with_opp_meta(app_client, mock_session):
    company = Company(id=2, name="OpenAI", classification="Client", category="SaaS / Tools")
    job = Job(
        id=2,
        company_id=2,
        dedupe_key="xyz789",
        external_id="ext-2",
        source="seo_jobs",
        title="Prompt Engineer",
        location="SF",
        url="https://example.com/job2",
        posted_at=None,
        scraped_at=None,
        description="OPP_META: athena_view=Client; confidence=0.95 || META: remote=onsite || Job description...",
        relevance_score=0.95,
        is_ai_search=True,
    )
    job.company = company
    
    mock_result = MagicMock()
    mock_result.first.return_value = (job, company)
    mock_session.execute.return_value = mock_result
    
    async with app_client as client:
        resp = await client.get("/api/jobs/2")
        assert resp.status_code == 200
        data = resp.json()
        assert "OPP_META:" in data["description"]
        assert "athena_view=Client" in data["description"]





@pytest.mark.asyncio
async def test_stats(app_client, mock_session):
    # Prepare five result objects corresponding to the five execute() calls
    r1 = MagicMock()
    r1.scalar_one.return_value = 10  # total_companies

    r2 = MagicMock()
    r2.scalar_one.return_value = 27  # total_jobs

    r3 = MagicMock()
    r3.scalar_one.return_value = 4   # total_competitors

    r4 = MagicMock()
    r4.scalar_one.return_value = 6   # total_clients

    r5 = MagicMock()
    r5.scalar_one.return_value = "2025-01-01T00:00:00"  # last_ingestion_at

    mock_session.execute.side_effect = [r1, r2, r3, r4, r5]

    async with app_client as client:
        resp = await client.get("/api/stats/")
        assert resp.status_code == 200
        data = resp.json()

        assert data["total_companies"] == 10
        assert data["total_jobs"] == 27
        assert data["total_competitors"] == 4
        assert data["total_clients"] == 6
        assert data["last_ingestion_at"] == "2025-01-01T00:00:00"
