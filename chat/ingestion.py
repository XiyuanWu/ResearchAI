from .document_loader import load_document, split_document
from .embeddings import embed_chunks
from .vector_store import store_chunks

# 7.4 File Upload & RAG Integration (Automatic ingestion)
def ingest_document(file_path: str, original_name: str):

    # 1. load saved file
    document = load_document(file_path)
    document["source"] = original_name # use original filename instead if uuid unique filename

    # 2. split the document into chunks
    chunks = split_document(document)
    if not chunks: raise ValueError("Document has no chunks")

    # 3. generate embedding vector
    embedded_chunks = embed_chunks(chunks)

    # 4. store chunks and vectors in Chroma
    stored_count = store_chunks(embedded_chunks)

    return {
        "source": original_name,
        "chunk_count": len(chunks),
        "stored_count": stored_count
    }