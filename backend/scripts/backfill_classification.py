import asyncio
from sqlalchemy import select
from src.db.session import get_session
from src.db.models import Company
from src.semantic.classifier_company import company_classifier

async def backfill_classifications():
    print("Starting backfill...")
    async for session in get_session():
        # Fetch ALL companies to re-apply new stricter/looser rules
        stmt = select(Company)
        result = await session.execute(stmt)
        companies = result.scalars().all()
        
        print(f"Found {len(companies)} companies to re-classify.")
        
        for company in companies:
            # Re-classify
            # Note: We might not have description easily if it's not stored on Company model explicitly
            # but usually it's inferred from jobs or just name. 
            # Classifier supports optional description.
            classification = company_classifier.classify(company.name)
            
            # Update only if different to output helpful logs
            if company.classification != classification:
                 print(f"Updating '{company.name}': {company.classification} -> {classification}")
                 company.classification = classification

            # v0: populate category if missing
            if not company.category:
                company.category = "Agency / Consultancy" if company.classification == "Competitor" else "SaaS / Tools"
            
        await session.commit()
        print("Backfill complete.")

if __name__ == "__main__":
    asyncio.run(backfill_classifications())
