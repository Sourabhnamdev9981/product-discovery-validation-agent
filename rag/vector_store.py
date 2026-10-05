# Stores product-research chunks in Chroma
# and retrieves the most relevant chunks for a query.

import chromadb

# Creates a local persistent Chroma database.
client = chromadb.PersistentClient(path="data/chroma")


# Creates or loads our product-research collection.
collection = client.get_or_create_collection(name="product_research")


def add_documents(
    chunks: list[str],
    embeddings: list[list[float]],
) -> None:
    """Store text chunks and their embeddings."""

    if not chunks:
        return

    ids = [f"chunk_{i}" for i in range(len(chunks))]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
    )


def retrieve_documents(
    query_embedding: list[float],
    n_results: int = 3,
) -> list[str]:
    """Retrieve the most relevant stored chunks."""

    if not query_embedding:
        return []

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )

    return results["documents"][0]
