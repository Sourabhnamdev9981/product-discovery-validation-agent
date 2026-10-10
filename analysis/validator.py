# Converts discovery findings into structured product-validation recommendations.

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from analysis.validation_schema import ProductValidation

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")


def parse_validation(response: dict) -> ProductValidation:
    # Validate the model output against the strict schema.
    return ProductValidation.model_validate(response)


def validate_product(
    analysis: dict,
    product_idea: str,
) -> ProductValidation:
    # Generate evidence-aware validation recommendations using Groq.

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in the .env file.")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )

    analysis_text = json.dumps(analysis, indent=2)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a product validation analyst. "
                    "Use only the provided discovery analysis and product idea. "
                    "Do not claim that user interviews or experiments have "
                    "already happened. Treat assumptions as unverified. "
                    "Recommend a small MVP and practical experiments that "
                    "could validate the highest-risk assumptions. "
                    "Do not treat online discussion as proof of demand."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Product idea:\n{product_idea}\n\n"
                    f"Discovery analysis:\n{analysis_text}\n\n"
                    "Produce structured product-validation recommendations."
                ),
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "product_validation",
                "strict": True,
                "schema": ProductValidation.model_json_schema(),
            },
        },
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("Groq returned an empty response.")

    return parse_validation(json.loads(content))
