import pytest
from src.semantic.classifier import AISearchClassifier
from src.semantic.classifier_company import CompanyClassifier

def test_company_classifier_heuristics():
    c = CompanyClassifier()
    
    # Test Hard Competitor Hints
    assert c.classify("Foobar SEO Agency") == "Competitor"
    assert c.classify("Digital Marketing Solutions Inc") == "Competitor" # has marketing
    assert c.classify("Elite Staffing Group") == "Competitor" # staffing

    # Test Clear Client Hints
    assert c.classify("Acme Software Inc") == "Client"
    assert c.classify("Cloud Platform Corp") == "Client"
    assert c.classify("MySaaS App") == "Client"

    # Test Conflict (Agency wins if explicit, but check logic)
    # "Digital Marketing Software" -> has "marketing" (comp) and "software" (client)
    # Our logic: 1) Hard comp hints win unless "inc/labs/etc" is present? 
    # Actually logic is: 
    # if has_comp and not has_neg_client: Competitor
    # if has_neg_client and not has_comp: Client
    # else: Embedding
    
    # "SEO Agency Software" -> has "seo agency" (comp) and "software" (neg_client) -> Fallback to embedding
    # We won't assert exact fallback here as it depends on embedding, but we can integrity check logic paths.

def test_company_classifier_embedding_fallback():
    c = CompanyClassifier()
    # A name with no keywords
    # "Anthropic" -> probably Client
    # "Randstad" -> probably Competitor (recruiting)
    # Just ensure it returns a string
    res = c.classify("Some Random Name")
    assert res in ["Client", "Competitor"]

def test_role_tiers():
    c = AISearchClassifier()
    
    # High confidence
    assert c.tier("Head of AI Search") == "core_ai_search"
    assert c.tier("SEO Manager") == "core_ai_search" # "SEO Manager" is in positive seeds? No, "SEO Specialist" is. 
    # Wait, POSITIVE_SEEDS has "SEO Manager" in Step 75
    
    # Medium confidence
    # Maybe something tangential?
    # "Content Writer" -> might be related or out of scope depending on embedding
    
    # Out of scope
    assert c.tier("Janitor") == "out_of_scope"
    assert c.tier("HR Director") == "out_of_scope"
