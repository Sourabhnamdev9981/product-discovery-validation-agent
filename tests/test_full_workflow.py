# Tests the complete LangGraph workflow using mocked external services.

from unittest.mock import patch

from main import app
from analysis.schema import DiscoveryAnalysis
from analysis.validation_schema import ProductValidation


def test_full_workflow():
    fake_search_result = {
        "code": "200",
        "data": {
            "webPages": {
                "value": [
                    {
                        "name": "Product Discovery Guide",
                        "url": "https://example.com/discovery",
                        "text": (
                            "Founders research users and competitors "
                            "before building products."
                        ),
                        "siteName": "Example",
                        "displayUrl": "example.com",
                    }
                ]
            }
        },
    }

    fake_analysis = {
        "problem_findings": [
            {
                "statement": (
                    "Founders need evidence before investing "
                    "heavily in a product."
                ),
                "evidence_indexes": [0],
            }
        ],
        "user_findings": [
            {
                "statement": "Founders are the initial target users.",
                "evidence_indexes": [0],
            }
        ],
        "competitor_findings": [],
        "assumptions": [
            "Founders will use an automated product discovery tool."
        ],
        "opportunities": [
            {
                "statement": (
                    "Provide evidence-backed product validation reports."
                ),
                "evidence_indexes": [0],
            }
        ],
    }

    fake_validation = {
        "assumptions": [
            "Founders will use an automated product discovery tool."
        ],
        "mvp_features": [
            "Evidence-backed product discovery report"
        ],
        "validation_experiments": [
            {
                "assumption": (
                    "Founders will use an automated product discovery tool."
                ),
                "experiment": (
                    "Test the product with a small group of founders "
                    "and measure report usefulness."
                ),
                "success_signal": (
                    "Target users report that the generated report "
                    "helps them make product decisions."
                ),
                "priority": "high",
            }
        ],
    }

    with (
        patch(
            "main.search_web",
            return_value=fake_search_result,
        ) as mock_search,
        patch(
            "main.analyze_evidence",
            return_value=DiscoveryAnalysis.model_validate(fake_analysis),
        ),
        patch(
            "main.validate_product",
            return_value=ProductValidation.model_validate(fake_validation),
        ),
    ):
        result = app.invoke(
            {
                "product_idea": (
                    "An AI tool that helps founders validate product ideas"
                ),
                "status": "",
                "message": "",
                "research_questions": [],
                "evidence": [],
                "search_count": 0,
                "analysis": {},
                "validation": {},
                "report": {},
            }
        )

    assert result["status"] == "ready"
    assert len(result["research_questions"]) == 5
    assert len(result["evidence"]) == 5

    # The workflow should search for each of its five research questions.
    assert mock_search.call_count == 5

    assert result["analysis"]["problem_findings"]
    assert result["analysis"]["assumptions"]
    assert result["analysis"]["opportunities"]

    assert result["validation"]["assumptions"]
    assert result["validation"]["mvp_features"]
    assert result["validation"]["validation_experiments"]

    assert result["report"]["product_idea"] == (
        "An AI tool that helps founders validate product ideas"
    )
    assert result["report"]["key_problems"]
    assert result["report"]["target_users"]
    assert result["report"]["assumptions"]
    assert result["report"]["opportunities"]
    assert result["report"]["mvp_features"]
    assert result["report"]["validation_experiments"]

    # The five searches return the same page, so it is listed once and every
    # cited finding points at it.
    report = result["report"]
    assert [source["url"] for source in report["sources"]] == [
        "https://example.com/discovery"
    ]
    assert report["cited_findings"]["key_problems"][0]["source_ids"] == [1]
    assert report["cited_findings"]["opportunities"][0]["source_ids"] == [1]
    assert report["cited_findings"]["competitor_findings"] == []
