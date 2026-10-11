# Tests the FastAPI endpoints without calling external services.

from fastapi.testclient import TestClient

from api import api

client = TestClient(api)


def test_health_check():
    # Verify that the API reports a healthy status.
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_discover_endpoint():
    # Verify the discover endpoint with a mocked workflow result.
    fake_result = {
        "status": "ready",
        "message": "Final product discovery report generated.",
        "report": {
            "product_idea": "An AI tool that helps founders validate product ideas",
            "key_problems": ["Founders need evidence before building."],
            "target_users": ["Founders"],
            "competitor_findings": [],
            "assumptions": ["Founders will use the tool."],
            "opportunities": ["Evidence-backed validation."],
            "mvp_features": ["Discovery report"],
            "validation_experiments": ["Test with founders."],
        },
    }

    from unittest.mock import patch

    with patch("api.app.invoke", return_value=fake_result):
        response = client.post(
            "/discover",
            json={
                "product_idea": (
                    "An AI tool that helps founders validate product ideas"
                )
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ready"
    assert data["message"] == "Final product discovery report generated."
    assert data["report"]["product_idea"] == (
        "An AI tool that helps founders validate product ideas"
    )


def test_discover_reports_groq_limit_errors():
    # Groq size/rate-limit failures become a clear 503 instead of a bare 500.
    from unittest.mock import patch

    from analysis.groq_client import GroqLimitError

    with patch(
        "api.app.invoke",
        side_effect=GroqLimitError("Groq rate limit reached."),
    ):
        response = client.post("/discover", json={"product_idea": "An idea"})

    assert response.status_code == 503
    assert response.json() == {"detail": "Groq rate limit reached."}


def test_discover_reports_provider_failures_as_503():
    # Groq outages, cut-off output and LangSearch failures share one 503 path.
    from unittest.mock import patch

    from analysis.groq_client import GroqError
    from rag.web_search import SearchError

    for error in [
        GroqError("Groq is temporarily unavailable. Try again later."),
        SearchError("LangSearch request failed. Try again later."),
    ]:
        with patch("api.app.invoke", side_effect=error):
            response = client.post("/discover", json={"product_idea": "An idea"})

        assert response.status_code == 503
        assert response.json() == {"detail": str(error)}


def test_unexpected_errors_return_generic_500_without_detail():
    # Unexpected failures must not expose their message (which may hold keys).
    from unittest.mock import patch

    unsafe_client = TestClient(api, raise_server_exceptions=False)

    with patch(
        "api.app.invoke",
        side_effect=RuntimeError("GROQ_API_KEY=gsk_example leaked"),
    ):
        response = unsafe_client.post("/discover", json={"product_idea": "An idea"})

    assert response.status_code == 500
    assert "gsk_example" not in response.text
