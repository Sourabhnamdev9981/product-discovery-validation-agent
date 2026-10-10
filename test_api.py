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
