from sklearn.cluster import KMeans
import numpy as np
from .embedder import embedder

def cluster_companies(company_texts: dict[str, str], n_clusters: int = 3):
    """
    company_texts: {company_name: concatenated_job_titles}
    Returns: {company_name: cluster_id}
    """
    if not company_texts:
        return {}
        
    names = list(company_texts.keys())
    texts = list(company_texts.values())
    
    if len(texts) < n_clusters:
         # Fallback if too few samples
         return {name: 0 for name in names}

    X = embedder.encode(texts)
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = km.fit_predict(X)
    return {name: int(label) for name, label in zip(names, labels)}

CLUSTER_LABELS = {
    0: "SaaS / Tools",
    1: "Agency / Consultancy",
    2: "In-house / Brand",
}
