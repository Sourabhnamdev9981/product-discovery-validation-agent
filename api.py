# Exposes the Product Discovery & Validation Agent through FastAPI.

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from analysis.groq_client import GroqError
from main import graph
from rag.web_search import SearchError

app = FastAPI(
    title="Product Discovery & Validation Agent",
    version="1.0.0",
)


# CORS: allows the local Vite frontend during development.
# Add your deployed Vercel frontend URL before production use.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://product-discovery-validation-agent.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DiscoveryRequest(BaseModel):
    """Defines the input accepted by the discovery endpoint."""

    product_idea: str


@app.get("/health")
def health_check() -> dict:
    """Confirms that the API is running."""

    return {"status": "ok"}


@app.post("/discover")
def discover_product(request: DiscoveryRequest) -> dict:
    """Runs the discovery workflow for the submitted product idea."""

    try:
        result = graph.invoke(
            {
                "product_idea": request.product_idea,
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
    except (GroqError, SearchError) as error:
        # Return a safe response for expected provider failures.
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    return {
        "status": result["status"],
        "message": result["message"],
        "report": result["report"],
    }
