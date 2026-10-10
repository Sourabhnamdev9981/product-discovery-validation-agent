# Tests that RapidAPI results can be converted
# into the evidence format used by our agent.

from rag.web_search import search_web, normalize_results


def test_product_discovery_search():
    result = search_web("AI product discovery tools", num_results=5)

    assert result["status"] == "OK"

    evidence = normalize_results(result)

    assert len(evidence) > 0

    first_result = evidence[0]

    assert "title" in first_result
    assert "url" in first_result
    assert "snippet" in first_result
    assert first_result["title"]
    assert first_result["url"]
