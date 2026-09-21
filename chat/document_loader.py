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