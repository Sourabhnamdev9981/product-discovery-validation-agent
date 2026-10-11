# Tests that structured analysis is validated
# without making a real Groq API request.

from analysis.analyzer import parse_analysis


def test_parse_valid_analysis():
    response = {
        "problem_findings": [
            {
                "statement": "Founders need better ways to evaluate product ideas.",
                "evidence_indexes": [0, 2],
            }
        ],
        "user_findings": [],
        "competitor_findings": [],
        "assumptions": ["Founders are willing to use automated validation."],
        "opportunities": [
            {
                "statement": "Provide evidence-backed product validation.",
                "evidence_indexes": [0, 2],
            }
        ],
    }

    result = parse_analysis(response)

    assert result.problem_findings[0].evidence_indexes == [0, 2]
