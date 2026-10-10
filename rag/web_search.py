# Sends product-discovery research queries to RapidAPI
# and returns the search response as structured JSON.

import os
import http.client
from urllib import response
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "real-time-web-search.p.rapidapi.com")


def search_web(query: str, num_results: int = 10) -> dict:
    """Search the web using RapidAPI."""

    if not RAPIDAPI_KEY:
        raise ValueError("RAPIDAPI_KEY is not set in the .env file.")

    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
    }

    path = (
        "/search"
        f"?q={query.replace(' ', '%20')}"
        f"&num={num_results}"
        "&start=0"
        "&gl=in"
        "&hl=en"
        "&location=India"
        "&device=desktop"
        "&nfpr=0"
        "&nhr=1"
        "&fetch_ai_overviews=false"
        "&return_organic_result_video_thumbnail=false"
    )

    conn.request("GET", path, headers=headers)

    response = conn.getresponse()
    data = response.read().decode("utf-8")

    if response.status == 429:
        raise RuntimeError(
            "RapidAPI monthly quota has been exceeded. "
            "Web search is temporarily unavailable."
        )

    if response.status != 200:
        raise RuntimeError(
            f"RapidAPI request failed: {response.status} {data}"
        )

    import json

    return json.loads(data)

# Converts RapidAPI search results into a simple evidence format
# that the product-discovery agent can use.


def normalize_results(result: dict) -> list[dict]:
    """Convert raw RapidAPI results into clean evidence records."""

    organic_results = result.get("data", {}).get("organic_results", [])

    evidence = []

    for item in organic_results:
        evidence.append(
            {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("snippet", ""),
                "source": item.get("source", ""),
                "domain": item.get("domain", ""),
            }
        )

    return evidence
