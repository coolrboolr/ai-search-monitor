import numpy as np
from .embedder import embedder

POSITIVE_SEEDS = [
    "AI SEO Specialist",
    "Head of Generative Search",
    "Answer Engine Optimization Lead",
    "LLM-powered SEO Strategist",
    "Search Engineer",
    "SEO Specialist",
    "SEO Manager",
    "Technical SEO",
    "Head of AI Search"
]

class AISearchClassifier:
    def __init__(self, threshold: float = 0.35): # Lowered threshold to capture more SEO roles potentially pivoting to AI
        self.threshold = threshold
        self.high_conf = 0.50
        self.medium_conf = 0.35
        self._pos_centroid = self._compute_centroid(POSITIVE_SEEDS)

    def _compute_centroid(self, texts):
        vecs = embedder.encode(texts)
        return np.mean(vecs, axis=0)
    
    def tier(self, title: str, description: str | None = None) -> str:
        s = self.score(title, description)
        if s >= self.high_conf:
            return "core_ai_search"
        if s >= self.medium_conf:
            return "related_search_or_seo"
        return "out_of_scope"

    def score(self, title: str, description: str | None = None) -> float:
        # Heavily weight title
        text = title 
        if description:
             text = f"{title}. {description[:200]}" # Truncate description for speed/noise
             
        v = embedder.encode([text])[0]
        return float(np.dot(v, self._pos_centroid))

    def is_relevant(self, title: str, description: str | None = None) -> bool:
        return self.score(title, description) >= self.threshold

classifier = AISearchClassifier()
