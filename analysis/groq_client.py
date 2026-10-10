# Shared Groq request settings and error handling for the
# analysis and validation stages.

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import APIStatusError, OpenAI

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

# Output budget per request, including the model's reasoning tokens.
MAX_COMPLETION_TOKENS = int(os.getenv("GROQ_MAX_COMPLETION_TOKENS", "2048"))

# gpt-oss models accept "low", "medium" or "high". Set it to an empty
# value when using a model that does not support reasoning effort.
REASONING_EFFORT = os.getenv("GROQ_REASONING_EFFORT", "low")


class GroqLimitError(RuntimeError):
    """Groq rejected a request because of its size or rate limits."""


def create_structured_completion(
    messages: list[dict],
    schema_name: str,
    schema: dict,
) -> str:
    """Send one strict structured-output request and return its JSON text."""

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in the .env file.")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )

    options = {"reasoning_effort": REASONING_EFFORT} if REASONING_EFFORT else {}

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_completion_tokens=MAX_COMPLETION_TOKENS,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": schema_name,
                    "strict": True,
                    "schema": schema,
                },
            },
            **options,
        )
    except APIStatusError as error:
        # Retrying an identical request cannot succeed, so fail clearly.
        if error.status_code == 413:
            raise GroqLimitError(
                f"The {schema_name} request is larger than the Groq model's "
                "token limit. Lower ANALYSIS_MAX_EVIDENCE_CHARS or "
                "GROQ_MAX_COMPLETION_TOKENS."
            ) from error

        if error.status_code == 429:
            retry_after = error.response.headers.get("retry-after")
            wait = f" Try again in {retry_after} seconds." if retry_after else ""
            raise GroqLimitError(
                f"Groq rate limit reached during {schema_name}.{wait}"
            ) from error

        raise

    choice = response.choices[0]

    if choice.finish_reason == "length":
        raise RuntimeError(
            f"Groq stopped the {schema_name} response at the "
            "GROQ_MAX_COMPLETION_TOKENS limit before it was complete."
        )

    if not choice.message.content:
        raise RuntimeError("Groq returned an empty response.")

    return choice.message.content
