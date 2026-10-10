# Tests that product-discovery analysis follows
# the strict structured-output schema.

from analysis.schema import DiscoveryAnalysis


def test_discovery_analysis_schema():
    result = DiscoveryAnalysis(
        problem_findings=[
            {
                "statement": "Founders need better ways to evaluate product ideas.",
                "evidence_indexes": [0, 2],
            }
        ],
        user_findings=[],
        competitor_findings=[],
        assumptions=["Founders are willing to use automated validation."],
        opportunities=["Provide evidence-backed product validation."],
    )

    assert len(result.problem_findings) == 1
    assert result.problem_findings[0].evidence_indexes == [0, 2]
    assert len(result.assumptions) == 1
    assert len(result.opportunities) == 1
