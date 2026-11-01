from io import BytesIO

from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from app.api.deps import DbSession, User
from app.core.config import get_settings
from app.models.image import ImageRow
from app.schemas.image import ImageOut
from app.services.storage import save_upload

router = APIRouter(prefix="/images", tags=["images"])


@router.post("", response_model=ImageOut, status_code=201)
async def upload(db: DbSession, user: User, file: UploadFile = File(...)):
    settings = get_settings()
    data = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if not data:
        raise HTTPException(400, "The uploaded file is empty")
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, "Image exceeds the upload size limit")
    try:
        image = Image.open(BytesIO(data))
        image.verify()
        image = Image.open(BytesIO(data))
        width, height = image.size
        image_format = image.format
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise HTTPException(400, "The uploaded file is not a valid image") from exc
    if image_format not in {"PNG", "JPEG", "WEBP", "GIF"}:
        raise HTTPException(400, "Unsupported image format")
    suffix = {"JPEG": ".jpg"}.get(image_format, f".{image_format.lower()}")
    key = save_upload(data, suffix)
    mime_type = {"PNG": "image/png", "JPEG": "image/jpeg", "WEBP": "image/webp", "GIF": "image/gif"}[image_format]
    row = ImageRow(user_id=user.id, storage_key=key, mime_type=mime_type, width=width, height=height)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
