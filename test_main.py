# Tests the Product Discovery Agent workflow,
# including validation, planning, and RAG evidence retrieval.

from unittest import result
from main import app
from main import app, validate_idea, plan_research
from unittest.mock import patch

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
    result = app.invoke(make_input("   "))

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

    with patch("main.search_web") as mock_search:
        mock_search.return_value = {
            "status": "OK",
            "data": {"organic_results": fake_evidence},
        }

        result = app.invoke(state)

    assert len(result["evidence"]) == 5
    assert result["search_count"] == 5
    assert mock_search.call_count == 5

    assert result["evidence"][0]["title"] == "AI Product Discovery Guide"
    assert result["evidence"][0]["url"] == "https://example.com/product-discovery"
    assert result["evidence"][0]["research_question"]
    assert result["evidence"][0]["evidence_status"] == "verified"
    assert result["evidence"][0]["claim"]
    assert result["evidence"][0]["source_type"] == "web_search_result"
    assert result["evidence"][0]["retrieved_at"]
