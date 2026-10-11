# Keeps search results that have the fields needed to cite them, and attaches
# source metadata. It does not check that a source supports any claim.

from datetime import datetime, timezone


def link_evidence(evidence: list[dict]) -> list[dict]:
    """Keep citable evidence and attach source metadata."""

    linked = []

    for item in evidence:
        title = item.get("title", "").strip()
        url = item.get("url", "").strip()
        snippet = item.get("snippet", "").strip()

        if not title or not url or not snippet:
            continue

        linked.append(
            {
                **item,
                # Copy of the snippet, not an extracted or checked claim.
                "claim": snippet,
                "evidence_status": "source_linked",
                "source_type": "web_search_result",
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    return linked
