# Tests the real Groq structured-output integration
# using a small product-discovery evidence set.
#
# LIVE TEST: calls the Groq API and consumes quota.
# Run with: RUN_LIVE_TESTS=1 python -m pytest -m live test_groq_analysis.py

import os

import pytest

from analysis.analyzer import analyze_evidence


@pytest.mark.live
def test_groq_analysis():
    if not os.getenv("GROQ_API_KEY"):
        pytest.skip("GROQ_API_KEY is not set in .env; cannot run the live Groq test.")

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
            "evidence_status": "source_linked",
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
            "evidence_status": "source_linked",
        },
    ]

    result = analyze_evidence(evidence)

    assert result.problem_findings is not None
    assert result.user_findings is not None
    assert result.competitor_findings is not None
    assert result.assumptions is not None
    assert result.opportunities is not None

    # analyze_evidence already rejects out-of-range indexes; double-check here.
    findings = (
        result.problem_findings
        + result.user_findings
        + result.competitor_findings
        + result.opportunities
    )
    for finding in findings:
        assert finding.evidence_indexes
        assert all(0 <= index < len(evidence) for index in finding.evidence_indexes)
