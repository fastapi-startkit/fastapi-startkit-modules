import uuid
from pathlib import Path

from fastapi import Request, UploadFile, File
from fastapi.responses import JSONResponse

UPLOAD_DIR = Path("public") / "img"
ALLOWED_MIME_PREFIXES = ("image/jpeg", "image/png", "image/gif", "image/webp")


async def upload(request: Request, photo: UploadFile = File(...)) -> JSONResponse:
    """Save an uploaded profile photo and return its public path."""
    if not photo.content_type or not photo.content_type.startswith("image/"):
        return JSONResponse(
            content={"error": "Only image files are allowed."},
            status_code=422,
        )

    ext = Path(photo.filename or "upload").suffix.lower() or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    dest = UPLOAD_DIR / filename

    contents = await photo.read()
    dest.write_bytes(contents)

    return JSONResponse(content={"path": f"/img/{filename}"})
