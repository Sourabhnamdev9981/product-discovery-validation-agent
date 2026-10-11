from rag.evidence import link_evidence

def test_link_evidence():
    evidence = [
        {
            "title": "Product Discovery Guide",
            "url": "https://example.com/guide",
            "snippet": "Product discovery helps teams understand user problems.",
        },
        {
            "title": "",
            "url": "https://example.com/missing-title",
            "snippet": "This result is incomplete.",
        },
    ]

    linked = link_evidence(evidence)

    assert len(linked) == 1
    assert linked[0]["title"] == "Product Discovery Guide"
    assert linked[0]["claim"] == linked[0]["snippet"]
    assert linked[0]["evidence_status"] == "source_linked"
    assert linked[0]["source_type"] == "web_search_result"
    assert linked[0]["retrieved_at"]
