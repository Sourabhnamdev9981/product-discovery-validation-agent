# Converts discovery findings into structured product-validation recommendations.

import json

from analysis.groq_client import create_structured_completion
from analysis.validation_schema import ProductValidation


def parse_validation(response: dict) -> ProductValidation:
    # Validate the model output against the strict schema.
    return ProductValidation.model_validate(response)


def validate_product(
    analysis: dict,
    product_idea: str,
) -> ProductValidation:
    # Generate evidence-aware validation recommendations using Groq.
    # The analysis is itself model output capped by GROQ_MAX_COMPLETION_TOKENS,
    # so this request stays small; compact JSON avoids indentation overhead.

    analysis_text = json.dumps(analysis, ensure_ascii=False)

    content = create_structured_completion(
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
        schema_name="product_validation",
        schema=ProductValidation.model_json_schema(),
    )

    return parse_validation(json.loads(content))
