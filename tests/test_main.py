# Tests the Product Discovery Agent workflow,
# including validation, planning, and RAG evidence retrieval.

from unittest.mock import patch

from analysis.schema import DiscoveryAnalysis
from analysis.validation_schema import ProductValidation
from main import graph, validate_idea, plan_research

EMPTY_ANALYSIS = DiscoveryAnalysis(
    problem_findings=[],
    user_findings=[],
    competitor_findings=[],
    assumptions=[],
    opportunities=[],
)

EMPTY_VALIDATION = ProductValidation(
    assumptions=[],
    mvp_features=[],
    validation_experiments=[],
)

def make_input(idea: str) -> dict:
    """Create the initial state required by the agent."""

    return {
        "product_idea": idea,
        "status": "",
        "message": "",
        "research_questions": [],
        "evidence": [],
        "search_count": 0,
    }


def test_valid_idea_creates_research_plan():
    state = make_input("AI product discovery assistant")

    validated = validate_idea(state)
    result = plan_research(validated)

    assert validated["status"] == "ready"
    assert len(result["research_questions"]) == 5


def test_empty_idea_skips_planning():
    result = graph.invoke(make_input("   "))

    assert result["status"] == "needs_input"
    assert result["research_questions"] == []
    assert result["evidence"] == []


def test_agent_retrieves_web_evidence():
    state = make_input("An AI tool that helps founders validate product ideas")

    fake_evidence = [
        {
            "title": "AI Product Discovery Guide",
            "url": "https://example.com/product-discovery",
            "snippet": "AI can help teams research and validate product ideas.",
            "source": "Example",
            "domain": "example.com",
        }
    ]

    # Search is the subject of this test. Analysis and validation are
    # mocked so the graph can finish without calling Groq.
    with (
        patch("main.search_web") as mock_search,
        patch("main.analyze_evidence", return_value=EMPTY_ANALYSIS),
        patch("main.validate_product", return_value=EMPTY_VALIDATION),
    ):
        mock_search.return_value = {
            "code": "200",
            "data": {
                "webPages": {
                    "value": [
                        {
                            "name": "AI Product Discovery Guide",
                            "url": "https://example.com/product-discovery",
                            "text": "AI can help teams research and validate product ideas.",
                            "siteName": "Example",
                            "displayUrl": "example.com",
                        }
                    ]
                }
            },
        }

        result = graph.invoke(state)

    assert len(result["evidence"]) == 5
    assert result["search_count"] == 5
    assert mock_search.call_count == 5

    assert result["evidence"][0]["title"] == "AI Product Discovery Guide"
    assert result["evidence"][0]["url"] == "https://example.com/product-discovery"
    assert [item["research_question"] for item in result["evidence"]] == (
        result["research_questions"]
    )
    assert result["evidence"][0]["evidence_status"] == "source_linked"
    assert result["evidence"][0]["claim"]
    assert result["evidence"][0]["source_type"] == "web_search_result"
    assert result["evidence"][0]["retrieved_at"]
