import asyncio
import sys
import os

from sqlalchemy import select

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.db.session import AsyncSessionLocal
from src.db.models import Company

async def main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Company).order_by(Company.classification, Company.category, Company.name))
        companies = result.scalars().all()
        print("ID | Classification | Category           | Name")
        print("--------------------------------------------------------")
        for c in companies:
            print(f"{c.id:3d} | {c.classification or '-':11s} | { (c.category or '-')[:18]:18s} | {c.name}")

if __name__ == "__main__":
    asyncio.run(main())
