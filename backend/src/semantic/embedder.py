from typing import Iterable
import numpy as np
from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self):
        # Load small, efficient model
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    def encode(self, texts: Iterable[str]) -> np.ndarray:
        return self.model.encode(list(texts), normalize_embeddings=True)

# Singleton instance
embedder = Embedder()
