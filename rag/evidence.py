# Converts verified search results into traceable evidence records
# with explicit claims and provenance.

from datetime import datetime, timezone


def verify_evidence(evidence: list[dict]) -> list[dict]:
    """Keep usable evidence and attach provenance metadata."""

    verified = []

    for item in evidence:
        title = item.get("title", "").strip()
        url = item.get("url", "").strip()
        snippet = item.get("snippet", "").strip()

        if not title or not url or not snippet:
            continue

        verified.append(
            {
                **item,
                "claim": snippet,
                "evidence_status": "verified",
                "source_type": "web_search_result",
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    return verified
