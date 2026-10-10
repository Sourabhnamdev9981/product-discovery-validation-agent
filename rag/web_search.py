# Searches the web with LangSearch and normalizes results for the agent.

import os

import requests
from dotenv import load_dotenv

load_dotenv()

LANGSEARCH_API_KEY = os.getenv("LANGSEARCH_API_KEY")
LANGSEARCH_URL = "https://api.langsearch.com/v1/web-search"


def search_web(query: str, num_results: int = 10) -> dict:
    """Search the web using LangSearch."""

    if not LANGSEARCH_API_KEY:
        raise ValueError("LANGSEARCH_API_KEY is not set in the .env file.")

    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    response = requests.post(
        LANGSEARCH_URL,
        headers={
            "Authorization": f"Bearer {LANGSEARCH_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "query": query,
            "count": max(1, min(num_results, 50)),
            "freshness": "noLimit",
            "contents": {"text": {"max_characters": 3000}},
        },
        timeout=30,
    )

    if response.status_code == 429:
        raise RuntimeError("LangSearch rate or usage limit reached.")

    if not response.ok:
        raise RuntimeError(f"LangSearch request failed: HTTP {response.status_code}.")

    result = response.json()

    if str(result.get("code")) != "200":
        raise RuntimeError(
            f"LangSearch search failed: {result.get('message', 'Unknown error')}"
        )

    return result


def normalize_results(result: dict) -> list[dict]:
    """Convert LangSearch pages into the agent's evidence format."""

    pages = result.get("data", {}).get("webPages", {}).get("value", [])
    evidence = []

    for item in pages:
        title = item.get("name", "")
        url = item.get("url", "")
        snippet = item.get("text") or item.get("snippet", "")

        if not title or not url or not snippet:
            continue

        evidence.append(
            {
                "title": title,
                "url": url,
                "snippet": snippet,
                "source": item.get("siteName", ""),
                "domain": item.get("displayUrl", ""),
            }
        )

    return evidence
