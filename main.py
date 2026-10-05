# Product Discovery Agent workflow:
# validates the product idea, creates research questions,
# and retrieves relevant evidence from the RAG knowledge base.

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from rag.embeddings import create_embeddings
from rag.vector_store import retrieve_documents


class AgentState(TypedDict):
    product_idea: str
    status: str
    message: str
    research_questions: list[str]
    evidence: list[str]


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


def retrieve_evidence(state: AgentState) -> dict:
    """Retrieve relevant product-research evidence for the first question."""

    question = state["research_questions"][0]

    query_embedding = create_embeddings([question])[0]

    evidence = retrieve_documents(
        query_embedding=query_embedding,
        n_results=3,
    )

    return {
        "evidence": evidence,
        "message": "Research plan created and evidence retrieved.",
    }


builder = StateGraph(AgentState)

builder.add_node("validate_idea", validate_idea)
builder.add_node("plan_research", plan_research)
builder.add_node("retrieve_evidence", retrieve_evidence)

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
builder.add_edge("retrieve_evidence", END)

app = builder.compile()


if __name__ == "__main__":
    result = app.invoke(
        {
            "product_idea": "An AI tool that helps founders validate product ideas",
            "status": "",
            "message": "",
            "research_questions": [],
            "evidence": [],
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
