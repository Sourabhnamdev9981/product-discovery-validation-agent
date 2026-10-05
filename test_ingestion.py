# Tests PDF text extraction and text chunking before we add embeddings.

from rag.ingestion import chunk_text


def test_chunk_text():
    text = "A" * 2500

    chunks = chunk_text(
        text,
        chunk_size=1000,
        chunk_overlap=200,
    )

    assert len(chunks) > 1
    assert all(len(chunk) <= 1000 for chunk in chunks)
# Tests that a real PDF can be read and converted into text chunks.

from rag.ingestion import chunk_text, extract_text_from_pdf


def test_pdf_extraction():
    text = extract_text_from_pdf("data/sample.pdf")

    assert text.strip()
    assert len(chunk_text(text)) > 0
