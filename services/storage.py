from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile, HTTPException, status

from config import SUPABASE_BUCKET, SUPABASE_BADGE_BUCKET, MAX_UPLOAD_SIZE
from services.supabase_client import get_supabase_client
from utils.badge_id import generate_badge_id

ALLOWED_BADGE_CONTENT_TYPES = ["image/png", "image/jpeg"]
CHUNK_SIZE = 1024 * 1024

async def upload_template(file: UploadFile) -> dict:
    client = get_supabase_client()
    storage = client.storage.from_(SUPABASE_BUCKET)

    file_bytes = await read_upload_with_limit(file)
    suffix = Path(file.filename or "template").suffix
    file_path = f"{uuid4().hex}{suffix}"

    storage.upload(
        file_path,
        file_bytes,
        file_options={"content-type": file.content_type or "application/octet-stream"},
    )

    public_url = storage.get_public_url(file_path)

    return {
        "file_path": file_path,
        "public_url": public_url,
        "filename": file.filename,
    }

async def upload_badge(file: UploadFile) -> dict:
    if file.content_type not in ALLOWED_BADGE_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid badge file type. Allowed types: {', '.join(ALLOWED_BADGE_CONTENT_TYPES)}",
        )

    client = get_supabase_client()
    storage = client.storage.from_(SUPABASE_BADGE_BUCKET)

    file_bytes = await read_upload_with_limit(file)
    suffix = Path(file.filename or "badge").suffix
    file_path = f"{generate_badge_id()}{suffix}"

    storage.upload(
        file_path,
        file_bytes,
        file_options={"content-type": file.content_type or "application/octet-stream"},
    )

    public_url = storage.get_public_url(file_path)

    return {
        "file_path": file_path,
        "public_url": public_url,
        "filename": file.filename,
    }

async def read_upload_with_limit(file: UploadFile, max_size: int = MAX_UPLOAD_SIZE) -> bytes:
    """Read an uploaded file in chunks, raising 413 if it exceeds max_size."""
    chunks = []
    total = 0
    while True:
        chunk = await file.read(CHUNK_SIZE)
        if not chunk:
            break
        total += len(chunk)
        if total > max_size:
            raise HTTPException(
                status_code=413,  # Payload too large
                detail=f"File too large. Maximum allowed size is {MAX_UPLOAD_SIZE // (1024 * 1024)}MB.",
            )
        chunks.append(chunk)
    return b"".join(chunks)
