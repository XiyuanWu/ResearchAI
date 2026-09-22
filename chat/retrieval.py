from .embeddings import embed_query
from .vector_store import get_collection

# 7.3 Retrieval & Answering (retrieve relevant chunks)
DISTANCE_THRESHOLD = 0.5

# retrieve the most relevant document chunks for a query
def retrieve_relevant_chunks(query: str, top_k: int = 3) -> list[dict]:
    query = query.strip()

    if not query: raise ValueError("Query not exists")
    if top_k <= 0: raise ValueError("top_k must be greater than 0")

    # 1. convert user's question to vector
    query_vector = embed_query(query)

    # 2. open the Chroma collection
    collections = get_collection()
    if collections.count() == 0: return []

    # 3. search for nearest document vector
    # top_k is only return most 3 relevant result
    results = collections.query(
        query_embeddings=[query_vector],
        n_results=min(top_k, collections.count()),
        include=["documents", "metadatas", "distances"]
    )

    # 4. convert Chroma's nested result into simple list
    # 0 mean only read first question
    relevant_chunks = []
    for index in range(len(results["ids"][0])): 
        # distance is for when a user question don't need a file, model response will not include about file
        distance = results["distances"][0][index]
        if distance > DISTANCE_THRESHOLD:
            continue
        relevant_chunks.append({
            "id": results["ids"][0][index],
            "text": results["documents"][0][index],
            "metadata": results["metadatas"][0][index],
            "distance": results["distances"][0][index]
        })

    return relevant_chunks