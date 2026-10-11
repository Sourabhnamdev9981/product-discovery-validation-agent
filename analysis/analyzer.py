# Validates product-discovery analysis and sends evidence
# to Groq when real LLM analysis is requested.

import json
import os
from collections.abc import Iterable
from itertools import zip_longest

from pydantic import ValidationError

from analysis.groq_client import GroqError, create_structured_completion
from analysis.schema import DiscoveryAnalysis

# Evidence budget for the analysis request. Groq's on-demand tier allows
# 8,000 tokens per minute for openai/gpt-oss-20b, a single larger request is
# rejected with HTTP 413, and the validation request follows within the same
# minute. 9,000 characters of compact JSON is roughly 2,300-3,000 tokens, which
# leaves room for the prompt and schema (~800 tokens), the completion budget
# (GROQ_MAX_COMPLETION_TOKENS) and the validation request.
MAX_EVIDENCE_ITEMS = int(os.getenv("ANALYSIS_MAX_EVIDENCE_ITEMS", "10"))
MAX_EXCERPT_CHARS = int(os.getenv("ANALYSIS_MAX_EXCERPT_CHARS", "500"))
MAX_EVIDENCE_CHARS = int(os.getenv("ANALYSIS_MAX_EVIDENCE_CHARS", "9000"))
MAX_TITLE_CHARS = 200


def shorten(text: str, limit: int) -> str:
    """Collapse whitespace and cut at a word boundary."""

    text = " ".join(text.split())

    if len(text) <= limit:
        return text

    return text[:limit].rsplit(" ", 1)[0] + "…"


def select_evidence(evidence: list[dict]) -> list[dict]:
    """Return a bounded, compact subset of the evidence for the model.

    Each record keeps the item's original position as "index", so the
    evidence_indexes the model cites refer to the unmodified evidence list.
    Items are taken round-robin across research questions so every
    question stays represented, then returned in original order.
    """

    groups: dict[str, list[int]] = {}

    for index, item in enumerate(evidence):
        groups.setdefault(item.get("research_question", ""), []).append(index)

    round_robin = [
        index
        for round_ in zip_longest(*groups.values())
        for index in round_
        if index is not None
    ]

    selected = []
    total_chars = 0

    for index in round_robin[:MAX_EVIDENCE_ITEMS]:
        item = evidence[index]
        record = {
            "index": index,
            "title": shorten(item["title"], MAX_TITLE_CHARS),
            "url": item["url"],
            "excerpt": shorten(item["snippet"], MAX_EXCERPT_CHARS),
        }
        size = len(json.dumps(record, ensure_ascii=False))

        if total_chars + size > MAX_EVIDENCE_CHARS:
            break

        selected.append(record)
        total_chars += size

    return sorted(selected, key=lambda record: record["index"])


def parse_analysis(
    response: dict,
    valid_indexes: Iterable[int] | None = None,
) -> DiscoveryAnalysis:
    """Validate structured analysis data.

    When valid_indexes is given, every finding must cite at least one
    evidence index, and only indexes from that set.
    """

    context = None if valid_indexes is None else {"valid_indexes": set(valid_indexes)}

    return DiscoveryAnalysis.model_validate(response, context=context)


def analyze_evidence(evidence: list[dict]) -> DiscoveryAnalysis:
    """Analyze product-discovery evidence using Groq."""

    # The input is reduced here, before the request, rather than after a
    # rejected request.
    selected = select_evidence(evidence)
    evidence_text = json.dumps(selected, ensure_ascii=False)

    content = create_structured_completion(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a product discovery analyst. "
                    "Analyze only the provided evidence. "
                    "Do not claim that user interviews occurred. "
                    "Do not treat discussion as proof of market demand.\n\n"
                    "Output format:\n"
                    "- problem_findings, user_findings, competitor_findings "
                    "and opportunities are lists of OBJECTS. Each object has "
                    'exactly two fields: "statement" (a concise, meaningful '
                    'sentence) and "evidence_indexes" (a non-empty list of '
                    "integers).\n"
                    "- Every opportunity must be an object with statement and "
                    "evidence_indexes, never a plain string.\n"
                    "- assumptions is a list of plain strings: unverified "
                    "hypotheses that the evidence does not establish.\n\n"
                    "Evidence rules:\n"
                    '- evidence_indexes may only contain the "index" values '
                    "of supplied evidence items that directly support the "
                    "statement. Never invent evidence indexes.\n"
                    "- Excerpts may be shortened. Do not speculate about "
                    "text that is not shown.\n"
                    "- Do not present an unsupported idea as an evidence-backed "
                    "finding or opportunity. If nothing in the evidence "
                    "supports it, leave it out or state it as an assumption.\n"
                    "- Return an empty list for any category that the "
                    "evidence does not support.\n\n"
                    "Return valid JSON that conforms exactly to the provided "
                    "schema."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Analyze the following product-discovery evidence "
                    "and produce the requested structured analysis.\n\n"
                    f"{evidence_text}"
                ),
            },
        ],
        schema_name="discovery_analysis",
        schema=DiscoveryAnalysis.model_json_schema(),
    )

    try:
        return parse_analysis(
            json.loads(content),
            valid_indexes=[record["index"] for record in selected],
        )
    except (json.JSONDecodeError, ValidationError) as error:
        # The model's output is invalid, so no analysis is returned.
        raise GroqError(
            "Groq's analysis did not match the expected format. Try again."
        ) from error
