from django.conf import settings
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# 8.3 RAG with LangChain (retriever)
COLLECTION_NAME = "research_documents"

def get_retriever(top_k: int = 3):
    if not settings.GEMINI_API_KEY: raise ValueError("GEMINI_API_KEY is missing")

    # convert user question to embedding/vector
    embeddings = GoogleGenerativeAIEmbeddings(
        model=settings.GEMINI_EMBEDDING_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        output_dimensionality=768
    )

    # open existing Chroma database
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(settings.CHROMA_PATH)
    )

    # search all chunks and return most relevant k result
    return vector_store.as_retriever(search_kwargs={"k": top_k})