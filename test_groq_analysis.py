# Tests the real Groq structured-output integration
# using a small product-discovery evidence set.

from analysis.analyzer import analyze_evidence


def test_groq_analysis():
    evidence = [
        {
            "title": "Product Discovery Guide",
            "url": "https://example.com/product-discovery",
            "snippet": (
                "Founders often use customer research and competitor analysis "
                "to evaluate product ideas before development."
            ),
            "source": "Example",
            "domain": "example.com",
            "research_question": ("What user problem would this product solve?"),
            "evidence_status": "verified",
        },
        {
            "title": "Startup Validation Guide",
            "url": "https://example.com/validation",
            "snippet": (
                "Early validation can help founders identify assumptions "
                "before investing heavily in product development."
            ),
            "source": "Example",
            "domain": "example.com",
            "research_question": ("What key assumptions remain unverified?"),
            "evidence_status": "verified",
        },
    ]

    result = analyze_evidence(evidence)

    assert result.problem_findings is not None
    assert result.user_findings is not None
    assert result.competitor_findings is not None
    assert result.assumptions is not None
    assert result.opportunities is not None
