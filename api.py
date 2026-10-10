# Exposes the product-discovery LangGraph workflow through FastAPI.

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from analysis.groq_client import GroqLimitError
from main import app

api = FastAPI(
    title="Product Discovery & Validation Agent",
    version="1.0.0",
)

api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DiscoveryRequest(BaseModel):
    # Defines the input accepted by the discovery endpoint.
    product_idea: str


@api.get("/health")
def health_check() -> dict:
    # Confirms that the API is running.
    return {"status": "ok"}


@api.post("/discover")
def discover_product(request: DiscoveryRequest) -> dict:
    # Runs the discovery workflow for the submitted product idea.
    try:
        result = app.invoke(
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
    except GroqLimitError as error:
        # Report Groq size/rate limits instead of a bare 500.
        raise HTTPException(status_code=503, detail=str(error)) from error

    return {
        "status": result["status"],
        "message": result["message"],
        "report": result["report"],
    }
