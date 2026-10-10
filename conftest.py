# Shared pytest setup. The default run is offline:
#   - tests marked "live" (LangSearch / Groq) are skipped unless RUN_LIVE_TESTS=1
#   - tests marked "model" (Hugging Face download, local Chroma store) are
#     skipped unless RUN_MODEL_TESTS=1
#   - in the default run, outbound TCP connections are refused as a safety net,
#     so an accidental real request fails loudly instead of spending quota.

import os
import socket

import pytest

RUN_LIVE = os.getenv("RUN_LIVE_TESTS") == "1"
RUN_MODEL = os.getenv("RUN_MODEL_TESTS") == "1"
LOOPBACK_HOSTS = {"127.0.0.1", "::1", "localhost"}


def _guarded_connect(original_connect):
    def connect(self, address):
        host = address[0] if isinstance(address, tuple) else address

        if host in LOOPBACK_HOSTS:
            return original_connect(self, address)

        raise RuntimeError(
            f"Network access to {host!r} is blocked in the offline test run. "
            "Live tests need RUN_LIVE_TESTS=1."
        )

    return connect


if not (RUN_LIVE or RUN_MODEL):
    socket.socket.connect = _guarded_connect(socket.socket.connect)


def pytest_collection_modifyitems(config, items):
    for item in items:
        if item.get_closest_marker("live") and not RUN_LIVE:
            item.add_marker(
                pytest.mark.skip(
                    reason="live API test; set RUN_LIVE_TESTS=1 to run it "
                    "(uses LangSearch / Groq quota)"
                )
            )

        if item.get_closest_marker("model") and not RUN_MODEL:
            item.add_marker(
                pytest.mark.skip(
                    reason="downloads a model or writes the local Chroma store; "
                    "set RUN_MODEL_TESTS=1 to run it"
                )
            )
