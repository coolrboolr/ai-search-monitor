from typing import Optional
from src.ingestion.sources.base import RawJob

def infer_remote_flag(text: str) -> Optional[str]:
    t = text.lower()
    if "remote" in t and any(w in t for w in ["anywhere", "global", "worldwide", "usa", "us"]):
        return "remote"
    if "hybrid" in t:
        return "hybrid"
    if "on-site" in t or "onsite" in t or "in-office" in t:
        return "onsite"
    return None

def infer_employment_type(text: str) -> Optional[str]:
    t = text.lower()
    if "full-time" in t or "full time" in t:
        return "full_time"
    if "part-time" in t or "part time" in t:
        return "part_time"
    if "contract" in t or "freelance" in t:
        return "contract"
    return None

def infer_seniority(text: str) -> Optional[str]:
    t = text.lower()
    if any(k in t for k in ["vp of", "vice president", "svp", "svp of", "executive vp"]):
        return "vp"
    if any(k in t for k in ["head of", "director", "director of"]):
        return "director"
    if any(k in t for k in ["lead ", "principal"]):
        return "lead"
    if any(k in t for k in ["senior", "sr. ", "sr "]):
        return "senior"
    if any(k in t for k in ["junior", "jr.", "jr "]):
        return "junior"
    return None

def infer_ai_signal(text: str) -> bool:
    t = text.lower()
    keywords = [
        "ai", "artificial intelligence", "llm", "large language model",
        "genai", "generative ai", "rag", "vector search", "semantic search",
        "answer engine", "ai search", "ai-powered search"
    ]
    return any(k in t for k in keywords)

def enrich_raw_job(raw_job: RawJob) -> RawJob:
    """
    Enrich RawJob in-place by populating structured metadata.
    Also appends a META prefix into description for legacy search support.
    """
    combined = (raw_job.title or "") + " || " + (raw_job.description or "")
    
    # Populate structured fields
    raw_job.remote_flag = infer_remote_flag(combined)
    raw_job.employment_type = infer_employment_type(combined)
    raw_job.seniority = infer_seniority(combined)
    raw_job.ai_forward = infer_ai_signal(combined)

    # Legacy Description Modification (Optional: can remove if UI exclusively uses columns)
    # Keeping it for v0 as search might rely on text content
    meta_bits = []
    if raw_job.remote_flag:
        meta_bits.append(f"remote={raw_job.remote_flag}")
    if raw_job.employment_type:
        meta_bits.append(f"type={raw_job.employment_type}")
    if raw_job.seniority:
        meta_bits.append(f"seniority={raw_job.seniority}")
    if raw_job.ai_forward:
        meta_bits.append("ai_forward=true")

    if meta_bits:
        meta_str = "META: " + " | ".join(meta_bits)
        existing = raw_job.description or ""
        # Avoid duplicate stamping if run multiple times
        if "META: " not in existing:
            raw_job.description = f"{meta_str} || {existing}".strip()
            
    return raw_job
