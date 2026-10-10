# Tests that analysis input is bounded before it reaches Groq, that evidence
# indexes keep pointing at the original evidence, and that Groq size/rate
# errors are reported clearly. No real API requests are made.

import json
from unittest.mock import MagicMock, patch

import httpx
import pytest
from openai import APIStatusError

from analysis import analyzer, groq_client
from analysis.analyzer import analyze_evidence, select_evidence
from analysis.groq_client import GroqLimitError, create_structured_completion

QUESTIONS = [f"Research question {number}?" for number in range(5)]


def make_evidence(per_question: int = 5, text_chars: int = 3000) -> list[dict]:
    # Mirrors the workflow's worst case: 5 searches x 5 results, each with
    # LangSearch's maximum page text and the duplicated "claim" field.
    text = ("word " * text_chars)[:text_chars]

    return [
        {
            "title": f"Result {question}-{result}",
            "url": f"https://example.com/{question}/{result}",
            "snippet": text,
            "claim": text,
            "source": "Example",
            "domain": "example.com",
            "research_question": QUESTIONS[question],
            "evidence_status": "verified",
            "source_type": "web_search_result",
            "retrieved_at": "2026-10-10T00:00:00+00:00",
        }
        for question in range(5)
        for result in range(per_question)
    ]


def test_large_evidence_is_bounded():
    evidence = make_evidence()
    selected = select_evidence(evidence)

    assert 0 < len(selected) <= analyzer.MAX_EVIDENCE_ITEMS
    assert len(json.dumps(selected, ensure_ascii=False)) <= analyzer.MAX_EVIDENCE_CHARS
    for record in selected:
        assert set(record) == {"index", "title", "url", "excerpt"}
        assert len(record["excerpt"]) <= analyzer.MAX_EXCERPT_CHARS + 1


def test_selected_indexes_point_to_original_evidence():
    evidence = make_evidence()
    selected = select_evidence(evidence)

    indexes = [record["index"] for record in selected]
    assert indexes == sorted(indexes)
    for record in selected:
        original = evidence[record["index"]]
        assert record["url"] == original["url"]
        assert record["title"] == original["title"]
        assert original["snippet"].startswith(record["excerpt"].rstrip("…"))


def test_selection_covers_every_research_question():
    evidence = make_evidence()
    selected = select_evidence(evidence)

    covered = {evidence[record["index"]]["research_question"] for record in selected}
    assert covered == set(QUESTIONS)


def test_short_evidence_is_sent_unchanged():
    evidence = make_evidence(per_question=1, text_chars=100)
    selected = select_evidence(evidence)

    assert [record["index"] for record in selected] == list(range(5))
    assert selected[0]["excerpt"] == " ".join(evidence[0]["snippet"].split())


def test_empty_evidence_selects_nothing():
    assert select_evidence([]) == []


def model_reply(payload: dict) -> str:
    return json.dumps(payload)


def test_analyze_evidence_sends_bounded_payload_and_validates_indexes():
    evidence = make_evidence()
    sent_indexes = [record["index"] for record in select_evidence(evidence)]
    reply = {
        "problem_findings": [
            {"statement": "A problem.", "evidence_indexes": [sent_indexes[-1]]}
        ],
        "user_findings": [],
        "competitor_findings": [],
        "assumptions": ["An assumption."],
        "opportunities": [
            {"statement": "An opportunity.", "evidence_indexes": sent_indexes[:2]}
        ],
    }

    with patch.object(
        analyzer, "create_structured_completion", return_value=model_reply(reply)
    ) as mock_completion:
        result = analyze_evidence(evidence)

    user_message = mock_completion.call_args.kwargs["messages"][1]["content"]
    full_payload = json.dumps(evidence)
    assert len(user_message) < analyzer.MAX_EVIDENCE_CHARS + 200
    assert len(user_message) < len(full_payload) / 10
    assert result.opportunities[0].evidence_indexes == sent_indexes[:2]


def test_analyze_evidence_rejects_index_not_sent_to_model():
    evidence = make_evidence()
    sent = {record["index"] for record in select_evidence(evidence)}
    unsent = next(index for index in range(len(evidence)) if index not in sent)
    reply = {
        "problem_findings": [{"statement": "A problem.", "evidence_indexes": [unsent]}],
        "user_findings": [],
        "competitor_findings": [],
        "assumptions": [],
        "opportunities": [],
    }

    with patch.object(
        analyzer, "create_structured_completion", return_value=model_reply(reply)
    ):
        with pytest.raises(ValueError):
            analyze_evidence(evidence)


def groq_error(status_code: int, headers: dict | None = None) -> APIStatusError:
    request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    response = httpx.Response(status_code, headers=headers or {}, request=request)
    return APIStatusError("Groq error", response=response, body=None)


def run_with_client_error(error: APIStatusError) -> tuple[MagicMock, GroqLimitError]:
    client = MagicMock()
    client.chat.completions.create.side_effect = error

    with (
        patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}),
        patch.object(groq_client, "OpenAI", return_value=client),
    ):
        with pytest.raises(GroqLimitError) as raised:
            create_structured_completion([], "discovery_analysis", {})

    return client, raised.value


def test_request_too_large_is_reported_without_retry():
    client, error = run_with_client_error(groq_error(413))

    assert "larger than the Groq model's token limit" in str(error)
    assert client.chat.completions.create.call_count == 1


def test_rate_limit_reports_retry_after():
    client, error = run_with_client_error(groq_error(429, {"retry-after": "12"}))

    assert "Try again in 12 seconds" in str(error)
    assert client.chat.completions.create.call_count == 1


def test_request_sets_completion_budget():
    client = MagicMock()
    choice = MagicMock(finish_reason="stop")
    choice.message.content = "{}"
    client.chat.completions.create.return_value.choices = [choice]

    with (
        patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}),
        patch.object(groq_client, "OpenAI", return_value=client),
    ):
        assert create_structured_completion([], "discovery_analysis", {}) == "{}"

    kwargs = client.chat.completions.create.call_args.kwargs
    assert kwargs["max_completion_tokens"] == groq_client.MAX_COMPLETION_TOKENS
    assert kwargs["response_format"]["json_schema"]["strict"] is True


def test_truncated_completion_is_reported():
    client = MagicMock()
    choice = MagicMock(finish_reason="length")
    client.chat.completions.create.return_value.choices = [choice]

    with (
        patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}),
        patch.object(groq_client, "OpenAI", return_value=client),
    ):
        with pytest.raises(RuntimeError, match="GROQ_MAX_COMPLETION_TOKENS"):
            create_structured_completion([], "discovery_analysis", {})


def test_selected_indexes_resolve_to_the_same_sources_in_the_report():
    # End-to-end for the mapping: indexes chosen by select_evidence must
    # still point at the right page once the report is built from the
    # original, unsubset evidence list.
    from report.builder import build_report

    evidence = make_evidence()
    sent = [record["index"] for record in select_evidence(evidence)]
    reply = {
        "problem_findings": [
            {"statement": "A problem.", "evidence_indexes": [sent[-1]]}
        ],
        "user_findings": [],
        "competitor_findings": [
            {"statement": "A rival.", "evidence_indexes": [sent[0], sent[1]]}
        ],
        "assumptions": [],
        "opportunities": [],
    }

    with patch.object(
        analyzer, "create_structured_completion", return_value=json.dumps(reply)
    ):
        analysis = analyze_evidence(evidence).model_dump()

    report = build_report("An idea", analysis, {}, evidence=evidence)

    problem_url = evidence[sent[-1]]["url"]
    assert report.cited_findings.key_problems[0].source_ids == [
        next(s.id for s in report.sources if s.url == problem_url)
    ]
    competitor_urls = {
        next(s.url for s in report.sources if s.id == source_id)
        for source_id in report.cited_findings.competitor_findings[0].source_ids
    }
    assert competitor_urls == {evidence[sent[0]]["url"], evidence[sent[1]]["url"]}
