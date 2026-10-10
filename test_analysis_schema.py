# Tests that product-discovery analysis follows
# the strict structured-output schema.

import pytest
from pydantic import ValidationError

from analysis.analyzer import parse_analysis
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
        opportunities=[
            {
                "statement": "Provide evidence-backed product validation.",
                "evidence_indexes": [0, 2],
            }
        ],
    )

    assert len(result.problem_findings) == 1
    assert result.problem_findings[0].evidence_indexes == [0, 2]
    assert len(result.assumptions) == 1
    assert len(result.opportunities) == 1


def make_analysis(opportunities: list) -> dict:
    return {
        "problem_findings": [],
        "user_findings": [],
        "competitor_findings": [],
        "assumptions": [],
        "opportunities": opportunities,
    }


def test_string_opportunities_are_rejected():
    # This is the exact shape Groq's model produced in the failing run.
    with pytest.raises(ValidationError):
        DiscoveryAnalysis.model_validate(
            make_analysis(["Develop an AI-powered platform for product validation."])
        )


def test_opportunities_are_in_the_json_schema_as_findings():
    schema = DiscoveryAnalysis.model_json_schema()

    assert schema["properties"]["opportunities"]["items"] == {
        "$ref": "#/$defs/Finding"
    }
    assert schema["properties"]["assumptions"]["items"] == {"type": "string"}


def test_valid_evidence_indexes_pass():
    result = parse_analysis(
        make_analysis([{"statement": "Opportunity.", "evidence_indexes": [0, 7]}]),
        valid_indexes=[0, 7, 12],
    )

    assert result.opportunities[0].evidence_indexes == [0, 7]


@pytest.mark.parametrize(
    ("indexes", "valid_indexes"),
    [
        ([3], range(3)),  # one past the end
        ([-1], range(3)),  # negative index
        ([], range(3)),  # no supporting evidence cited
        ([0], []),  # any citation is fabricated when there is no evidence
        ([1], [0, 2]),  # exists in the full list but was not sent to the model
    ],
)
def test_invalid_evidence_indexes_are_rejected(indexes, valid_indexes):
    with pytest.raises(ValidationError):
        parse_analysis(
            make_analysis([{"statement": "Opportunity.", "evidence_indexes": indexes}]),
            valid_indexes=valid_indexes,
        )


def test_empty_evidence_allows_only_empty_findings():
    result = parse_analysis(make_analysis([]), valid_indexes=[])

    assert result.opportunities == []
