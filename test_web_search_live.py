# Tests that LangSearch results can be converted
# into the evidence format used by our agent.
#
# LIVE TEST: calls the LangSearch API and consumes quota.
# Run with: RUN_LIVE_TESTS=1 python -m pytest -m live test_web_search_live.py

import os

import pytest

from rag.web_search import search_web, normalize_results


@pytest.mark.live
def test_product_discovery_search():
    if not os.getenv("LANGSEARCH_API_KEY"):
        pytest.skip(
            "LANGSEARCH_API_KEY is not set in .env; cannot run the live search test."
        )

    result = search_web("AI product discovery tools", num_results=5)

    # LangSearch signals success with code "200"; search_web already raises
    # for any other code, so this asserts the same contract explicitly.
    assert str(result["code"]) == "200"

    evidence = normalize_results(result)

    assert len(evidence) > 0

    first_result = evidence[0]

    assert "title" in first_result
    assert "url" in first_result
    assert "snippet" in first_result
    assert first_result["title"]
    assert first_result["url"]
