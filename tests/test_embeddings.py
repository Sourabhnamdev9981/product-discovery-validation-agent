# Tests that product-research text is converted into embeddings
# and that each embedding has the expected size.
#
# MODEL TEST: downloads the all-MiniLM-L6-v2 model on first run.
# Run with: RUN_MODEL_TESTS=1 python -m pytest -m model test_embeddings.py


import pytest


@pytest.mark.model
def test_create_embeddings():
    # Imported inside the test so collecting this file loads nothing.
    from rag.embeddings import create_embeddings

    chunks = [
        "Users need a simpler way to validate product ideas.",
        "Competitor research helps identify existing solutions.",
    ]

    embeddings = create_embeddings(chunks)

    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384
    assert len(embeddings[1]) == 384
