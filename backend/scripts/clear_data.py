import asyncio
import sys
import os
from sqlalchemy import text

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.db.session import AsyncSessionLocal

async def clear_data():
    print("Clearing all jobs and companies...")
    async with AsyncSessionLocal() as session:
        # Cascade delete should handle jobs if companies are deleted, 
        # but let's be explicit or use TRUNCATE if supported (pg) or DELETE (sqlite)
        # We don't know exact DB type for sure here (pg vs sqlite), so standard DELETE is safer
        await session.execute(text("DELETE FROM jobs"))
        await session.execute(text("DELETE FROM companies"))
        await session.commit()
    print("Data cleared.")

if __name__ == "__main__":
    asyncio.run(clear_data())
