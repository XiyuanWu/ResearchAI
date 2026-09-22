from pathlib import Path

# 7.1 Document Processing (load document)
ALLOWED_SUFFIXES = {".txt", ".md"}

def load_document(path: str | Path) -> dict:
    file_path = Path(path)

    #1. if file not exists
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    # 2. only allow file that ending with txt and md
    suffix = file_path.suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise ValueError(f"File type not allowed. Only txt and md are allowed. ")

    # 3. read as UTF-8 text
    try:
        text = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"File is not valid UTF-8 text: {file_path}") from exc

    text = text.strip()
    if not text:
        raise ValueError(f"File is empty: {file_path}")

    # 4. return text + metadata(file name)
    return {"text": text, "source": file_path.name}

# 7.2 Document Processing (split into chunks)
def split_document(document: dict, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[dict]:
    
    # 1. condition check
    if chunk_size <= 0: raise ValueError("Chunk size must be greater than 0")
    if chunk_overlap < 0: raise ValueError("Chunk overlap can not be negative")
    if chunk_overlap >= chunk_size: raise ValueError("Chunk overlap must smaller than chunk size")

    # 2. extract document info
    text = document["text"]
    source = document["source"]
    chunks = []

    start = 0           # chunk start index
    chunk_index = 0     # current chunk index

    # 3. loop, cut text and add into chunk
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append({
                "text": chunk_text,
                "source": source,
                "chunk_index": chunk_index
            })
            chunk_index += 1

        start += chunk_size - chunk_overlap

    return chunks