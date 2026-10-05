# Tests that product-research text is converted into embeddings
# and that each embedding has the expected size.

from rag.embeddings import create_embeddings


def test_create_embeddings():
    chunks = [
        "Users need a simpler way to validate product ideas.",
        "Competitor research helps identify existing solutions.",
    ]

    embeddings = create_embeddings(chunks)

    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384
    assert len(embeddings[1]) == 384
