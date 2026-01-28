import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException, status

from app.config import settings

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}


def ensure_storage_path() -> Path:
    storage_path = Path(settings.storage_path)
    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path


def save_photo(file: UploadFile) -> str:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported image type")

    content = file.file.read(settings.max_upload_bytes + 1)
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Photo too large")

    storage_path = ensure_storage_path()
    extension = ".jpg" if file.content_type == "image/jpeg" else ".png"
    filename = f"{uuid.uuid4()}{extension}"
    filepath = storage_path / filename
    with open(filepath, "wb") as f:
        f.write(content)
    return str(filepath)
