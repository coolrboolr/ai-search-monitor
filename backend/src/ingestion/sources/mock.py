from .base import Source, RawJob
import asyncio
from datetime import datetime, timedelta

class MockSource(Source):
    # Note: this source is not wired into the v0 ingestion pipeline; used for local demos/tests only.
    name = "mock"

    async def fetch(self):
        print("Running Mock Source...")
        base_date = datetime.now()
        
        jobs = [
            ("AI Search Engineer", "FutureCorp AI", "Remote", "Build RAG systems."),
            ("SEO Specialist for AI", "TechGiant", "San Francisco, CA", "Optimize for ChatGPT."),
            ("Head of Search", "StartupX", "New York, NY", "Lead search strategy."),
            ("Search Quality Evaluator", "Google", "Mountain View, CA", "Evaluate LLM outputs."),
            ("AI Content Strategist", "MediaCo", "London, UK", "Create AI-friendly content."),
            ("Machine Learning Engineer", "OpenAI", "San Francisco, CA", "Train reasoning models."),
            ("Technical SEO Manager", "AgencyOne", "Remote", "Fix crawl issues for AI bots."),
            ("Product Manager, Search", "Bing", "Redmond, WA", "Integrate Copilot into search."),
            ("Data Analyst", "DataCorp", "Austin, TX", "Analyze search trends."),
            ("Prompt Engineer", "PromptLy", "Remote", "Optimize prompts for SEO."),
            ("Frontend Developer", "WebStudio", "Berlin, DE", "Build websites. Not AI related."),
            ("Barista", "CoffeeShop", "Seattle, WA", "Make coffee."),
            ("Sales Representative", "SalesForce", "Chicago, IL", "Sell software."),
            ("HR Manager", "PeopleOps", "Remote", "Manage people.")
        ]

        for i, (title, company, loc, desc) in enumerate(jobs):
            yield RawJob(
                external_id=f"mock-{i}",
                title=title,
                company=company,
                location=loc,
                url=f"https://example.com/job{i}",
                source="mock",
                posted_at=(base_date - timedelta(days=i)).isoformat(),
                description=desc
            )
