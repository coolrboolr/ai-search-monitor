
from src.semantic.classifier_company import company_classifier, embedder
import numpy as np

def check(name, desc=None):
    text = name
    if desc:
         text = f"{name}. {desc[:200]}"
    v = embedder.encode([text])[0]
    c_score = float(np.dot(v, company_classifier._competitor_centroid))
    cl_score = float(np.dot(v, company_classifier._client_centroid))
    classification = company_classifier.classify(name, desc)
    print(f"'{name}' -> Comp: {c_score:.4f} | Client: {cl_score:.4f} | Diff: {c_score - cl_score:.4f} | Result: {classification}")

if __name__ == "__main__":
    check("Acme Digital Agency")
    check("Best SEO Consulting")
    check("Mannix Marketing", "We are a full-service digital marketing agency.")
    check("NoGood Digital Marketing Agency")
