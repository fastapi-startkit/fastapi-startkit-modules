import uuid
from pathlib import Path

from fastapi import UploadFile, File
from fastapi.responses import JSONResponse
from fastapi_startkit.storage import Storage


async def upload(photo: UploadFile = File(...)) -> JSONResponse:
    """Upload a profile photo to S3 and return its storage key."""
    if not photo.content_type or not photo.content_type.startswith("image/"):
        return JSONResponse(
            content={"error": "Only image files are allowed."},
            status_code=422,
        )

    ext = Path(photo.filename or "upload").suffix.lower() or ".jpg"
    filename = f"photos/{uuid.uuid4().hex}{ext}"

    contents = await photo.read()
    Storage.disk("s3").put(filename, contents)

    return JSONResponse(content={"path": filename, "url": Storage.disk("s3").url(filename)})


async def stream(path: str):
    """Stream a file from S3 back to the client."""
    return Storage.disk("s3").stream(path)
