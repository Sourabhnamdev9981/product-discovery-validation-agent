# Manual LangSearch check: prints a few live results for eyeballing.
# It replaces the old module-level script, which made a live request as soon
# as pytest imported the file.
#
# LIVE TEST: calls the LangSearch API and consumes quota.
# Run with: RUN_LIVE_TESTS=1 python -m pytest -m live -s test_langsearch_manual.py

import os

import pytest

from rag.web_search import normalize_results, search_web


@pytest.mark.live
def test_langsearch_manual_print():
    if not os.getenv("LANGSEARCH_API_KEY"):
        pytest.skip("LANGSEARCH_API_KEY is not set in .env; cannot run the live check.")

    result = search_web(
        "official documentation for AI interview preparation tools",
        num_results=3,
    )

    evidence = normalize_results(result)

    print(f"Normalized results: {len(evidence)}")

    for item in evidence:
        print(item["title"])
        print(item["url"])
        print(item["snippet"][:200])
        print("-" * 40)

    assert evidence
