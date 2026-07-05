import os
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_admin
from app.exceptions import NotFoundException
from app.models.auth import User
from app.models.media import Media, MediaFolder
from app.schemas.common import paginated_response, success_response

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads")

router = APIRouter(prefix="/media", tags=["Admin - Media"])


class MediaUpdate(BaseModel):
    filename: str | None = None
    alt_text: str | None = None
    title: str | None = None
    caption: str | None = None
    description: str | None = None
    folder_id: str | None = None
    is_active: bool | None = None


class MediaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    folder_id: str | None = None
    filename: str
    file_extension: str
    mime_type: str
    file_size_bytes: int
    storage_bucket: str
    storage_path: str
    public_url: str
    alt_text: str | None = None
    title: str | None = None
    caption: str | None = None
    description: str | None = None
    media_type: str
    width: int | None = None
    height: int | None = None
    dominant_color: str | None = None
    is_active: bool
    uploaded_by: str | None = None
    created_at: datetime
    updated_at: datetime


class FolderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    parent_id: str | None = None
    name: str
    slug: str
    description: str | None = None
    sort_order: int
    created_by: str | None = None
    created_at: datetime
    updated_at: datetime


@router.get("", response_model=dict)
def list_media(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    media_type: str | None = None,
    folder_id: str | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    query = db.query(Media).filter(Media.deleted_at.is_(None))
    if media_type:
        query = query.filter(Media.media_type == media_type)
    if folder_id:
        query = query.filter(Media.folder_id == folder_id)
    total = query.count()
    items = query.order_by(Media.created_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()
    return paginated_response(
        data=[MediaResponse.model_validate(m).model_dump() for m in items],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{id}", response_model=dict)
def get_media(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    media = db.query(Media).filter(Media.id == id, Media.deleted_at.is_(None)).first()
    if not media:
        raise NotFoundException("Media not found")
    return success_response(data=MediaResponse.model_validate(media).model_dump())


@router.post("/upload", response_model=dict)
def upload_media(
    file: UploadFile = File(...),
    folder_id: str | None = Form(None),
    alt_text: str | None = Form(None),
    title: str | None = Form(None),
    caption: str | None = Form(None),
    description: str | None = Form(None),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    file_ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    media_type = "image"
    if file.content_type:
        if file.content_type.startswith("image/"):
            media_type = "image"
        elif file.content_type.startswith("video/"):
            media_type = "video"
        elif file.content_type.startswith("audio/"):
            media_type = "audio"
        elif file.content_type.startswith("application/pdf"):
            media_type = "document"
        else:
            media_type = "other"

    file_bytes = file.file.read()
    file_size = len(file_bytes)

    file_id = str(uuid4())
    ext = file_ext if file_ext else "bin"
    saved_name = f"{file_id}.{ext}"
    relative_path = f"uploads/{saved_name}"
    abs_path = os.path.join(UPLOAD_DIR, saved_name)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "wb") as f:
        f.write(file_bytes)

    media = Media(
        filename=file.filename or "untitled",
        file_extension=file_ext,
        mime_type=file.content_type or "application/octet-stream",
        file_size_bytes=file_size,
        storage_bucket="local",
        storage_path=relative_path,
        public_url=f"/uploads/{saved_name}",
        alt_text=alt_text,
        title=title,
        caption=caption,
        description=description,
        media_type=media_type,
        folder_id=folder_id,
        uploaded_by=admin.id,
        is_active=True,
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return success_response(
        data=MediaResponse.model_validate(media).model_dump(),
        message="Media uploaded successfully",
    )


@router.put("/{id}", response_model=dict)
def update_media(
    id: str,
    request: MediaUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    media = db.query(Media).filter(Media.id == id, Media.deleted_at.is_(None)).first()
    if not media:
        raise NotFoundException("Media not found")
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(media, key, value)
    db.commit()
    db.refresh(media)
    return success_response(
        data=MediaResponse.model_validate(media).model_dump(),
        message="Media updated successfully",
    )


@router.get("/folders", response_model=dict)
def list_folders(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    folders = db.query(MediaFolder).filter(MediaFolder.deleted_at.is_(None)).order_by(MediaFolder.sort_order.asc()).all()
    return success_response(
        data=[FolderResponse.model_validate(f).model_dump() for f in folders],
        message="Folders retrieved",
    )


@router.delete("/{id}", response_model=dict)
def delete_media(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    media = db.query(Media).filter(Media.id == id, Media.deleted_at.is_(None)).first()
    if not media:
        raise NotFoundException("Media not found")
    media.deleted_at = datetime.now(UTC)
    db.commit()
    return success_response(message="Media deleted successfully")
