# Converts product-research text chunks into numerical vectors
# that can later be used for semantic search.

from sentence_transformers import SentenceTransformer

# Load the embedding model once so it can be reused.
model = SentenceTransformer("all-MiniLM-L6-v2")


def create_embeddings(chunks: list[str]) -> list[list[float]]:
    """Convert text chunks into embedding vectors."""
    if not chunks:
        return []

    embeddings = model.encode(chunks)

    return embeddings.tolist()
