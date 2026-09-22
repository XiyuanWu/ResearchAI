import chromadb
from django.conf import settings

# 7.2 Vector Search (vector database)
COLLECTION_NAME = "research_documents"

# open the local Chroma database and return the document collection
def get_collection():
    client = chromadb.PersistentClient(path=str(settings.CHROMA_PATH))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    return collection

# store embedded chunks in ChromaDB, and return the number of chunks stored
def store_chunks(embedded_chunks: list[dict]) -> int:
    if not embedded_chunks: return 0

    # four list needed for ChromaDB
    ids = []            # id of each chunk
    documents = []      # chunk text
    embeddings = []     # embedding of this chunk
    metadatas = []      # extra info: filename, chunk number

    for chunk in embedded_chunks:
        if "embedding" not in chunk:
            raise ValueError(f"Chunk {chunk.get("chunk_index")} has no embedding")

        source = chunk["source"]
        chunk_index = chunk["chunk_index"]

        ids.append(f"{source}: {chunk_index}")
        documents.append(chunk["text"])
        embeddings.append(chunk["embedding"])
        metadatas.append({
            "source": source,
            "chunk_index": chunk_index
        })

    collections = get_collection()
    collections.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return len(ids)
