from pathlib import Path
from uuid import uuid4
from django.conf import settings
from django.core.files.storage import default_storage

from .document_loader import ALLOWED_SUFFIXES

# 7.4 File Upload & RAG Integration (backend upload handling)
def save_uploaded_file(uploaded_file) -> dict:
    original_name = Path(uploaded_file.name).name
    suffix = Path(original_name).suffix.lower()

    # 1. condition check: file extension, file must non-empty and file size
    if suffix not in ALLOWED_SUFFIXES: raise ValueError("File type not supported")
    if uploaded_file.size == 0: raise ValueError("File is empty")
    if uploaded_file.size > settings.MAX_UPLOAD_SIZE: raise ValueError("File are too large. Maximum size is 2MB. ")

    # 2. create a unique storage name
    stored_name = (f"uploads/{uuid4().hex}_{original_name}")

    # 3. save under media path
    saved_name = default_storage.save(stored_name, uploaded_file)

    return {
        "original_name": original_name,
        "stored_name": saved_name,
        "absolute_path": default_storage.path(saved_name),
        "size": uploaded_file.size
    }