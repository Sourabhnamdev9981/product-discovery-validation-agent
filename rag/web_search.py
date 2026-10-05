# Searches the web for product-discovery research questions.
# This will later be connected to the LangGraph workflow.

import os

import requests

SEARCH_API_URL = "YOUR_RAPIDAPI_ENDPOINT"


def search_web(query: str) -> list[dict]:
    """Send a search query and return structured web results."""

    api_key = os.getenv("RAPIDAPI_KEY")

    if not api_key:
        raise RuntimeError("RAPIDAPI_KEY is not configured.")

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "YOUR_RAPIDAPI_HOST",
    }

    response = requests.get(
        SEARCH_API_URL,
        headers=headers,
        params={
            "query": query,
            "limit": 10,
        },
        timeout=15,
    )

    response.raise_for_status()

    return response.json()
