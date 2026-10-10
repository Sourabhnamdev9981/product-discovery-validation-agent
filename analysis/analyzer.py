# Validates product-discovery analysis and sends evidence
# to Groq when real LLM analysis is requested.

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from analysis.schema import DiscoveryAnalysis

# Load environment variables from the project root .env file.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

def parse_analysis(response: dict) -> DiscoveryAnalysis:
    """Validate structured analysis data."""

    return DiscoveryAnalysis.model_validate(response)


def analyze_evidence(evidence: list[dict]) -> DiscoveryAnalysis:
    """Analyze product-discovery evidence using Groq."""

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in the .env file.")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )

    evidence_text = json.dumps(evidence, indent=2)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a product discovery analyst. "
                    "Analyze only the provided evidence. "
                    "Do not claim that user interviews occurred. "
                    "Do not treat discussion as proof of market demand. "
                    "Clearly distinguish evidence-backed findings "
                    "from assumptions and opportunities."
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
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "discovery_analysis",
                "strict": True,
                "schema": DiscoveryAnalysis.model_json_schema(),
            },
        },
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("Groq returned an empty response.")

    return parse_analysis(json.loads(content))
