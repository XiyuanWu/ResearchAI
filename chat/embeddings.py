from django.conf import settings
from google import genai
from google.genai import types

# 7.2 Vector Search (embeddings)
# convert document chunk to vector
def embed_chunks(chunks: list[dict]) -> list[dict]:
    if not settings.GEMINI_API_KEY: raise ValueError("GEMINI_API_KEY is missing")
    if not chunks: return []

    texts = [chunk["text"] for chunk in chunks]
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    response = client.models.embed_content(
        model=settings.GEMINI_EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=768
        )
    )

    if not response.embeddings:
        raise ValueError("Embedding model returned no embeddings")
    if len(response.embeddings) != len(chunks):
        raise ValueError("Embedding count does not match chunk count")

    embedded_chunks = []
    for chunk, embedding in zip(chunks, response.embeddings):
        if not embedding.values: raise ValueError("Embedding vector is empty")

        embedded_chunks.append({
            **chunk, 
            "embedding": list(embedding.values)
        })
    return embedded_chunks

# convert user question to vector
def embed_query(query: str) -> list[float]:
    query = query.strip()

    if not query: raise ValueError("Query not exists")
    if not settings.GEMINI_API_KEY: raise ValueError("GEMINI_API_KEY is missing")

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    response = client.models.embed_content(
        model=settings.GEMINI_EMBEDDING_MODEL,
        contents=query,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY", 
            output_dimensionality=768
        )
    )

    if not response.embeddings or not response.embeddings[0].values:
        raise ValueError("Embedding model returned no embedding")

    return list(response.embeddings[0].values)