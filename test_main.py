# Tests the Product Discovery Agent workflow,
# including validation, planning, and RAG evidence retrieval.

from main import app


def make_input(idea: str) -> dict:
    """Create the initial state required by the agent."""

    return {
        "product_idea": idea,
        "status": "",
        "message": "",
        "research_questions": [],
        "evidence": [],
    }


def test_valid_idea_creates_research_plan():
    result = app.invoke(make_input("AI product discovery assistant"))

    assert result["status"] == "ready"
    assert len(result["research_questions"]) == 5


def test_empty_idea_skips_planning():
    result = app.invoke(make_input("   "))

    assert result["status"] == "needs_input"
    assert result["research_questions"] == []
    assert result["evidence"] == []


def test_agent_retrieves_rag_evidence():
    result = app.invoke(make_input("AI product discovery assistant"))

    assert len(result["evidence"]) > 0
