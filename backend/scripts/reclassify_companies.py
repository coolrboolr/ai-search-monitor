
import asyncio
import sys
import os

from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Add parent directory to path so we can import src
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.db.session import AsyncSessionLocal
from src.db.models import Company, Job
from src.semantic.classifier_company import company_classifier

async def reclassify_all():
    print("Starting company reclassification...")
    
    async with AsyncSessionLocal() as session:
        # Get all companies
        result = await session.execute(select(Company))
        companies = result.scalars().all()
        
        updated_count = 0
        
        for company in companies:
            # Fetch up to 5 job titles to form a description proxy
            job_stmt = (
                select(Job.title)
                .where(Job.company_id == company.id)
                .limit(5)
            )
            job_res = await session.execute(job_stmt)
            titles = job_res.scalars().all()
            
            description_text = ""
            if titles:
                lower_titles = [t.lower() for t in titles]
                tags = []

                if any("account manager" in t or "customer success" in t for t in lower_titles):
                    tags.append("client services agency")
                if any("head of seo" in t or "director of seo" in t or "seo director" in t for t in lower_titles):
                    tags.append("strong seo leadership")
                if any("performance marketing" in t or "paid media" in t for t in lower_titles):
                    tags.append("performance marketing")

                description_text = "Hiring for: " + ", ".join(titles)
                if tags:
                    description_text += ". Tags: " + ", ".join(tags)
            
            # Re-classify
            new_classification = company_classifier.classify(company.name, description_text)
            
            # Determine new category
            new_category = "Agency / Consultancy" if new_classification == "Competitor" else "SaaS / Tools"
            
            # Update fields
            company.classification = new_classification
            company.category = new_category
            
            print(f"[{company.id}] {company.name} -> {new_classification} ({new_category})")
            updated_count += 1
            
        await session.commit()
        print(f"\nDone! Reclassified {updated_count} companies.")

if __name__ == "__main__":
    asyncio.run(reclassify_all())
