print("1. Minimal start", flush=True)
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
print("2. Path appended", flush=True)

try:
    import src.core.config
    print("3. Imported config", flush=True)
except Exception as e:
    print(f"Error importing config: {e}", flush=True)

try:
    from src.db.session import AsyncSessionLocal
    print("4. Imported session", flush=True)
except Exception as e:
    print(f"Error importing session: {e}", flush=True)

try:
    from src.ingestion.upsert import upsert_raw_job
    print("5. Imported upsert", flush=True)
except Exception as e:
    print(f"Error importing upsert: {e}", flush=True)
