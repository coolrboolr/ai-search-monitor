import numpy as np
from .embedder import embedder

COMPETITOR_SEEDS = [
    "Digital Marketing Agency",
    "SEO Agency",
    "Recruitment Agency",
    "Staffing Firm",
    "IT Consultancy",
    "Interactive Agency",
    "Full Service Agency",
    "Search Marketing Firm",
    "Talent Acquisition Partner"
]

CLIENT_SEEDS = [
    "SaaS Platform",
    "Software Company",
    "E-commerce Brand",
    "Consumer Tech Product",
    "Financial Technology Platform",
    "Enterprise Software Solution",
    "Healthcare Technology"
]

COMPETITOR_KEYWORDS = [
    "agency", "agencies", "marketing", "digital marketing", "seo agency",
    "consulting", "consultancy", "studio", "creative", "media",
    "performance marketing", "recruitment", "staffing", "search marketing"
]

CLIENT_KEYWORDS = [
    "saas", "software", "platform", "app", "product", "tool", "suite",
    "cloud", "storage", "data platform", "analytics platform", "advisor",
    "labs", "ai", "systems", "solutions"
]

COMPETITOR_MARGIN = 0.05
# Heuristics
# "Client" hints that strongly suggest it's NOT an agency (e.g. products)
NEG_CLIENT_HINTS = [
    "labs", "systems", "cloud", "platform", "app",
    "software", "technologies", "technology", 
    # Removed "inc", "solutions", "group", "corp" as they are common in agencies too
]

COMP_HARD_HINTS = [
    "agency", "agencies", "marketing", "digital marketing", "seo agency",
    "consulting", "consultancy", "media group", "performance marketing",
    "creative agency", "advertising agency",
]

class CompanyClassifier:
    def __init__(self):
        self._competitor_centroid = self._compute_centroid(COMPETITOR_SEEDS)
        self._client_centroid = self._compute_centroid(CLIENT_SEEDS)

    def _compute_centroid(self, texts):
        vecs = embedder.encode(texts)
        return np.mean(vecs, axis=0)

    def classify(self, company_name: str, description: str | None = None) -> str:
        """
        Classifies a company as 'Competitor' or 'Client' using separate keyword heuristics + margin-based semantic similarity.
        """
        text = company_name
        if description:
             text = f"{company_name}. {description[:200]}"
        
        text_lower = text.lower()
        
        # 1. Keyword Heuristics
        has_client_kw = any(kw in text_lower for kw in CLIENT_KEYWORDS)
        has_comp_kw = any(kw in text_lower for kw in COMPETITOR_KEYWORDS)
        
        # Immediate Client override (strong signal)
        if has_client_kw and not has_comp_kw:
            return "Client"
            
        # 2. Semantic Scores
        text_lower = text.lower()
        
        has_comp = any(h in text_lower for h in COMP_HARD_HINTS)
        has_neg_client = any(h in text_lower for h in NEG_CLIENT_HINTS)

        # 1) Hard competitor hints win unless clearly product-ish
        if has_comp and not has_neg_client:
            return "Competitor"

        # 2) Clear product-ish without agency hints -> Client
        if has_neg_client and not has_comp:
            return "Client"

        v = embedder.encode([text])[0]
        
        score_competitor = float(np.dot(v, self._competitor_centroid))
        score_client = float(np.dot(v, self._client_centroid))
        
        # 3. Margin-based decision (Bias towards Client)
        if score_competitor >= score_client + COMPETITOR_MARGIN:
            return "Competitor"
        else:
            return "Client"

company_classifier = CompanyClassifier()
