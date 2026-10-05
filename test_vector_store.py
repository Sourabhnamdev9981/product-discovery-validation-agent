# Tests that our product-research chunks can be stored
# and retrieved from the local vector database.

from rag.embeddings import create_embeddings
from rag.vector_store import (
    add_documents,
    retrieve_documents,
)

# Tests whether a product-research question retrieves
# the relevant stored evidence.


def test_store_and_retrieve():
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
