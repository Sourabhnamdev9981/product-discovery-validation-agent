# Product Discovery Agent workflow:
# validates the product idea, creates research questions,
# and retrieves relevant evidence from the RAG knowledge base.

from analysis.analyzer import analyze_evidence
from langgraph.graph import END, START, StateGraph
from analysis.validator import validate_product
from rag.evidence import verify_evidence
from typing import TypedDict
from report.builder import build_report


class AgentState(TypedDict):
    product_idea: str
    status: str
    message: str
    research_questions: list[str]
    evidence: list[dict]
    search_count: int
    analysis: dict
    validation: dict
    report: dict


def validate_idea(state: AgentState) -> dict:
    """Check whether a product idea was provided."""

    idea = state["product_idea"].strip()

    if not idea:
        return {
            "product_idea": "",
            "status": "needs_input",
            "message": "Please provide a product idea.",
            "research_questions": [],
            "evidence": [],
        }

    return {
        "product_idea": idea,
        "status": "ready",
        "message": "Product idea accepted. Ready for discovery.",
        "research_questions": [],
        "evidence": [],
    }


def route_after_validation(state: AgentState) -> str:
    """Continue to planning only when the product idea is valid."""

    if state["status"] == "ready":
        return "plan"

    return "stop"


def plan_research(state: AgentState) -> dict:
    """Create a small, bounded set of product research questions."""

    questions = [
        f"What user problem would this product solve: {state['product_idea']}?",
        "Who experiences this problem, and in what situations?",
        "What existing products or alternatives address this problem?",
        "What credible evidence supports the problem and its importance?",
        "What key assumptions remain unverified and need user validation?",
    ]

    return {
        "research_questions": questions,
        "message": "Research plan created.",
    }


# Searches the web for the first research question
# and converts the results into agent-friendly evidence.
from rag.web_search import search_web, normalize_results


# Searches each research question within a strict API budget
# and combines the results into one evidence collection.

# Searches all planned questions, normalizes the results,
# and verifies the evidence before storing it in agent state.

MAX_SEARCHES = 5


def retrieve_evidence(state: AgentState) -> dict:
    """Collect and verify web evidence within the search budget."""

    evidence = []

    for question in state["research_questions"]:
        if state["search_count"] >= MAX_SEARCHES:
            break

        result = search_web(question, num_results=5)
        question_evidence = normalize_results(result)

        for item in question_evidence:
            item["research_question"] = question

        evidence.extend(question_evidence)
        state["search_count"] += 1

    verified_evidence = verify_evidence(evidence)

    return {
        "evidence": verified_evidence,
        "search_count": state["search_count"],
        "message": "Web research completed and evidence verified.",
    }


def analyze_product(state: AgentState) -> dict:
    # Analyze collected evidence and return structured findings.
    analysis = analyze_evidence(state["evidence"])

    return {
        "analysis": analysis.model_dump(),
        "message": "Product discovery analysis completed.",
    }


def validate_product_node(state: AgentState) -> dict:
    # Turn discovery findings into MVP and validation recommendations.
    validation = validate_product(
        state["analysis"],
        state["product_idea"],
    )

    return {
        "validation": validation.model_dump(),
        "message": "Product validation completed.",
    }


def generate_report(state: AgentState) -> dict:
    # Build the final report from validated workflow results.
    report = build_report(
        state["product_idea"],
        state["analysis"],
        state["validation"],
    )

    return {
        "report": report.model_dump(),
        "message": "Final product discovery report generated.",
    }


builder = StateGraph(AgentState)

builder.add_node("validate_idea", validate_idea)
builder.add_node("plan_research", plan_research)
builder.add_node("retrieve_evidence", retrieve_evidence)
builder.add_node("analyze_product", analyze_product)
builder.add_node("validate_product", validate_product_node)
builder.add_node("generate_report", generate_report)

builder.add_edge(START, "validate_idea")

builder.add_conditional_edges(
    "validate_idea",
    route_after_validation,
    {
        "plan": "plan_research",
        "stop": END,
    },
)

builder.add_edge("plan_research", "retrieve_evidence")
builder.add_edge("retrieve_evidence", "analyze_product")
builder.add_edge("analyze_product", "validate_product")
builder.add_edge("validate_product", "generate_report")
builder.add_edge("generate_report", END)

app = builder.compile()

if __name__ == "__main__":
    result = app.invoke(
        {
            "product_idea": "An AI tool that helps founders validate product ideas",
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

    print("Status:", result["status"])
    print("Message:", result["message"])

    print("\nResearch questions:")
    for number, question in enumerate(
        result["research_questions"],
        start=1,
    ):
        print(f"{number}. {question}")

    print("\nRetrieved evidence:")
    for number, evidence in enumerate(
        result["evidence"],
        start=1,
    ):
        print(f"{number}. {evidence}")
    print("\nFinal Product Discovery Report:")
    print(result["report"])
