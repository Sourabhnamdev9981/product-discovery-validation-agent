# Tests that our product-research chunks can be stored
# and retrieved from the local vector database.
#
# MODEL TEST: loads the embedding model and writes to data/chroma/.
# Run with: RUN_MODEL_TESTS=1 python -m pytest -m model test_vector_store.py
# Note: the stored chunk IDs are fixed, so a second run against the same
# data/chroma/ store fails with a duplicate-ID error until that folder is removed.

import pytest


# Tests whether a product-research question retrieves
# the relevant stored evidence.
@pytest.mark.model
def test_store_and_retrieve():
    # Imported inside the test: importing rag.vector_store opens the local store.
    from rag.embeddings import create_embeddings
    from rag.vector_store import add_documents, retrieve_documents

    chunks = [
        "Product discovery helps founders validate product ideas.",
        "Competitor research identifies existing solutions.",
    ]

    embeddings = create_embeddings(chunks)

    add_documents(chunks, embeddings)

    query = "How can founders validate an idea?"

    query_embedding = create_embeddings([query])[0]

    results = retrieve_documents(query_embedding, n_results=1)

    assert len(results) == 1
    assert "validate product ideas" in results[0]
