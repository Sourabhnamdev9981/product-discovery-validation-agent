from rag.evidence import verify_evidence

def test_verify_evidence():
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

    verified = verify_evidence(evidence)

    assert len(verified) == 1
    assert verified[0]["title"] == "Product Discovery Guide"
    assert verified[0]["claim"] == verified[0]["snippet"]
    assert verified[0]["evidence_status"] == "verified"
    assert verified[0]["source_type"] == "web_search_result"
    assert verified[0]["retrieved_at"]
