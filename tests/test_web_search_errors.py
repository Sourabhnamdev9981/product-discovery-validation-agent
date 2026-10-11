# Tests that LangSearch failures raise SearchError with a safe message.
# requests.post is mocked, so no real request is made.

from unittest.mock import MagicMock, patch

import pytest
import requests

from rag import web_search
from rag.web_search import SearchError, search_web


def fake_response(status_code: int, body: dict | None = None) -> MagicMock:
    response = MagicMock(status_code=status_code, ok=status_code < 400)
    response.json.return_value = body or {}
    return response


def run_search(**kwargs) -> SearchError:
    with (
        patch.object(web_search, "LANGSEARCH_API_KEY", "secret-key"),
        patch.object(web_search.requests, "post", **kwargs),
    ):
        with pytest.raises(SearchError) as raised:
            search_web("product discovery")

    return raised.value


def test_rate_limit_is_reported():
    error = run_search(return_value=fake_response(429))

    assert "rate or usage limit" in str(error)


def test_server_error_is_reported_without_status_detail():
    error = run_search(return_value=fake_response(500))

    assert str(error) == "LangSearch request failed. Try again later."


def test_connection_failure_is_reported():
    error = run_search(side_effect=requests.ConnectionError("connect to 10.0.0.1 failed"))

    assert str(error) == "LangSearch could not be reached. Try again later."
    assert "10.0.0.1" not in str(error)


def test_provider_error_message_is_not_passed_on():
    body = {"code": 500, "message": "internal detail from provider"}
    error = run_search(return_value=fake_response(200, body))

    assert "internal detail" not in str(error)
    assert str(error) == "LangSearch could not complete the search. Try again later."


def test_unreadable_body_is_reported():
    response = fake_response(200)
    response.json.side_effect = ValueError("not json")
    error = run_search(return_value=response)

    assert str(error) == "LangSearch returned an unreadable response."


def test_successful_search_returns_result():
    body = {"code": "200", "data": {"webPages": {"value": []}}}

    with (
        patch.object(web_search, "LANGSEARCH_API_KEY", "secret-key"),
        patch.object(web_search.requests, "post", return_value=fake_response(200, body)),
    ):
        assert search_web("product discovery") == body
