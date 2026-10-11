# Tests that analysis findings are flattened into report strings and that
# their supporting sources survive into the report. Offline only.

import json

import pytest

from report.builder import build_report

EVIDENCE = [
    {
        "title": "Founder research guide",
        "url": "https://example.com/guide",
        "snippet": "Founders research users first.",
        "domain": "example.com",
        "research_question": "q1",
    },
    {
        "title": "Interview prep tools",
        "url": "https://example.org/tools",
        "snippet": "Students use mock interview apps.",
        "domain": "example.org",
        "research_question": "q2",
    },
    {
        # Same page as index 0, returned for a different research question.
        "title": "Founder research guide",
        "url": "https://example.com/guide",
        "snippet": "Founders research users first.",
        "domain": "example.com",
        "research_question": "q3",
    },
]


def make_analysis(**overrides) -> dict:
    analysis = {
        "problem_findings": [
            {"statement": "Founders lack evidence.", "evidence_indexes": [0]}
        ],
        "user_findings": [
            {"statement": "Early-stage founders.", "evidence_indexes": [1]}
        ],
        "competitor_findings": [],
        "assumptions": ["Founders will pay for reports."],
        "opportunities": [
            {"statement": "Evidence-backed reports.", "evidence_indexes": [0, 1]}
        ],
    }
    analysis.update(overrides)
    return analysis


VALIDATION = {
    "assumptions": ["Founders will pay for reports."],
    "mvp_features": ["Discovery report"],
    "validation_experiments": [
        {
            "assumption": "Founders will pay for reports.",
            "experiment": "Run a paid pilot with ten founders.",
            "success_signal": "Three founders pay.",
            "priority": "high",
        }
    ],
}


def test_build_report_converts_findings_to_statements():
    report = build_report("An idea", make_analysis(), VALIDATION)

    assert report.opportunities == ["Evidence-backed reports."]
    assert report.key_problems == ["Founders lack evidence."]
    assert report.target_users == ["Early-stage founders."]
    assert report.competitor_findings == []
    assert report.assumptions == ["Founders will pay for reports."]
    assert report.validation_experiments == ["Run a paid pilot with ten founders."]
    assert report.mvp_features == ["Discovery report"]


def test_citations_resolve_to_sources_with_deduplicated_urls():
    report = build_report("An idea", make_analysis(), VALIDATION, evidence=EVIDENCE)

    # Index 0 and 2 share a URL, so there are two sources, not three.
    assert [source.url for source in report.sources] == [
        "https://example.com/guide",
        "https://example.org/tools",
    ]
    assert [source.id for source in report.sources] == [1, 2]
    assert report.sources[0].title == "Founder research guide"
    assert report.sources[0].domain == "example.com"

    assert report.cited_findings.key_problems[0].source_ids == [1]
    assert report.cited_findings.target_users[0].source_ids == [2]
    assert report.cited_findings.opportunities[0].source_ids == [1, 2]


def test_legacy_string_fields_match_cited_statements():
    report = build_report("An idea", make_analysis(), VALIDATION, evidence=EVIDENCE)

    assert report.key_problems == [
        c.statement for c in report.cited_findings.key_problems
    ]
    assert report.opportunities == [
        c.statement for c in report.cited_findings.opportunities
    ]


def test_assumptions_and_recommendations_are_never_sourced():
    report = build_report("An idea", make_analysis(), VALIDATION, evidence=EVIDENCE)
    dumped = report.model_dump()

    assert "assumptions" not in dumped["cited_findings"]
    assert "mvp_features" not in dumped["cited_findings"]
    assert report.assumptions == ["Founders will pay for reports."]


def test_out_of_range_citation_fails_loudly():
    analysis = make_analysis(
        problem_findings=[{"statement": "Bad.", "evidence_indexes": [3]}]
    )

    with pytest.raises(ValueError, match="evidence index 3"):
        build_report("An idea", analysis, VALIDATION, evidence=EVIDENCE)


def test_without_evidence_findings_have_no_linked_sources():
    # Callers that do not pass evidence get findings without citations
    # rather than guessed ones.
    report = build_report("An idea", make_analysis(), VALIDATION)

    assert report.sources == []
    assert report.cited_findings.key_problems[0].source_ids == []
    assert report.cited_findings.opportunities[0].source_ids == []


def test_finding_without_indexes_is_not_linked():
    analysis = make_analysis(
        user_findings=[{"statement": "Unsourced.", "evidence_indexes": []}]
    )

    report = build_report("An idea", analysis, VALIDATION, evidence=EVIDENCE)

    assert report.cited_findings.target_users[0].source_ids == []


def test_empty_evidence_with_empty_findings_builds_cleanly():
    analysis = make_analysis(
        problem_findings=[],
        user_findings=[],
        competitor_findings=[],
        opportunities=[],
    )

    report = build_report("An idea", analysis, VALIDATION, evidence=[])

    assert report.sources == []
    assert report.opportunities == []


def test_report_with_citations_serializes_to_json():
    report = build_report("An idea", make_analysis(), VALIDATION, evidence=EVIDENCE)

    payload = json.loads(report.model_dump_json())

    assert payload["sources"][0]["url"] == "https://example.com/guide"
    assert payload["cited_findings"]["opportunities"][0]["source_ids"] == [1, 2]
    # Original contract fields are still present with their original types.
    for field in (
        "product_idea",
        "key_problems",
        "target_users",
        "competitor_findings",
        "assumptions",
        "opportunities",
        "mvp_features",
        "validation_experiments",
    ):
        assert field in payload
