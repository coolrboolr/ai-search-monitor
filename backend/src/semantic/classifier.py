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
    "Technical SEO"
]

class AISearchClassifier:
    def __init__(self, threshold: float = 0.35): # Lowered threshold to capture more SEO roles potentially pivoting to AI
        self.threshold = threshold
        self._pos_centroid = self._compute_centroid(POSITIVE_SEEDS)

    def _compute_centroid(self, texts):
        vecs = embedder.encode(texts)
        return np.mean(vecs, axis=0)

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
