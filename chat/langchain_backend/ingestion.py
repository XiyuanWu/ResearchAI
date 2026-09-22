from pathlib import Path
from django.conf import settings
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from chat.langchain_backend.rag import COLLECTION_NAME
from chat.manual_backend.document_loader import ALLOWED_SUFFIXES

# 8.3 RAG with LangChain (document processing)
ALLOWED_SUFFIXES = {".txt", ".md"}

def ingest_document(file_path: str, original_name: str):
    path = Path(file_path)
    if path.suffix.lower() not in ALLOWED_SUFFIXES:
        raise ValueError("Only .txt and .md are supported")

    # 1. load the saved file
    documents = TextLoader(str(path), encoding="utf-8").load()
    if not documents or not documents[0].page_content.strip():
        raise ValueError("Document is empty")

    # 2. split document into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)
    if not chunks: raise ValueError("Document has no chunks")

    for index, chunk in enumerate(chunks):
        chunk.metadata["source"] = original_name
        chunk.metadata["chunk_index"] = index

    # 3. convert chunks to embeddings/vector
    embeddings = GoogleGenerativeAIEmbeddings(
        model=settings.GEMINI_EMBEDDING_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        output_dimensionality=768
    )

    # 4. store embeddings/vector into Chroma database
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(settings.CHROMA_PATH)
    )
    vector_store.add_documents(chunks)

    return {
        "source": original_name,
        "chunk_count": len(chunks),
        "stored_count": len(chunks)
    }

