import asyncio
from sqlalchemy import select, func
from src.db.session import get_session
from src.db.models import Company

async def check_classifications():
    async for session in get_session():
        stmt = select(Company.classification, func.count(Company.id)).group_by(Company.classification)
        result = await session.execute(stmt)
        for classification, count in result.all():
            print(f"Classification: {classification}, Count: {count}")

if __name__ == "__main__":
    asyncio.run(check_classifications())
