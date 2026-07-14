from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_admin
from app.exceptions import NotFoundException
from app.models.auth import User
from app.models.content import Guide
from app.schemas.common import paginated_response, success_response
from app.utils.slug import generate_slug

router = APIRouter(prefix="/guides", tags=["Admin - Guides"])


class GuideCreate(BaseModel):
    title: str
    slug: str | None = None
    word_count: int | None = None
    category_id: str | None = None
    author_id: str | None = None
    reviewer_id: str | None = None
    subtitle: str | None = None
    excerpt: str | None = None
    content: str | None = None
    cover_image_url: str | None = None
    reading_time_minutes: int | None = None
    difficulty_level: str | None = None
    is_featured: bool = False
    is_active: bool = True
    is_published: bool = False
    status: str = "draft"
    published_at: datetime | None = None
    scheduled_at: datetime | None = None
    sort_order: int = 0


class GuideUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    word_count: int | None = None
    category_id: str | None = None
    author_id: str | None = None
    reviewer_id: str | None = None
    subtitle: str | None = None
    excerpt: str | None = None
    content: str | None = None
    cover_image_url: str | None = None
    reading_time_minutes: int | None = None
    difficulty_level: str | None = None
    is_featured: bool | None = None
    is_active: bool | None = None
    is_published: bool | None = None
    status: str | None = None
    published_at: datetime | None = None
    scheduled_at: datetime | None = None
    sort_order: int | None = None


class GuideResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    slug: str
    category_id: str | None = None
    author_id: str | None = None
    reviewer_id: str | None = None
    subtitle: str | None = None
    excerpt: str | None = None
    content: str | None = None
    cover_image_url: str | None = None
    reading_time_minutes: int | None = None
    difficulty_level: str | None = None
    is_featured: bool
    is_active: bool
    is_published: bool
    status: str
    view_count: int = 0
    word_count: int = 0
    published_at: datetime | None = None
    scheduled_at: datetime | None = None
    sort_order: int
    created_at: datetime
    updated_at: datetime


@router.get("", response_model=dict)
def list_guides(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str | None = None,
    category_id: str | None = None,
    author_id: str | None = None,
    difficulty_level: str | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    query = db.query(Guide).filter(Guide.deleted_at.is_(None))
    if status:
        query = query.filter(Guide.status == status)
    if category_id:
        query = query.filter(Guide.category_id == category_id)
    if author_id:
        query = query.filter(Guide.author_id == author_id)
    if difficulty_level:
        query = query.filter(Guide.difficulty_level == difficulty_level)
    total = query.count()
    items = query.order_by(Guide.created_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()
    return paginated_response(
        data=[GuideResponse.model_validate(g).model_dump() for g in items],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{id}", response_model=dict)
def get_guide(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    guide = db.query(Guide).filter(Guide.id == id, Guide.deleted_at.is_(None)).first()
    if not guide:
        raise NotFoundException("Guide not found")
    return success_response(data=GuideResponse.model_validate(guide).model_dump())


@router.post("", response_model=dict)
def create_guide(
    request: GuideCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    data = request.model_dump(exclude_unset=True)
    if not data.get("slug"):
        data["slug"] = generate_slug(data.get("title", ""), Guide, db)
    guide = Guide(**data)
    db.add(guide)
    db.commit()
    db.refresh(guide)
    return success_response(
        data=GuideResponse.model_validate(guide).model_dump(),
        message="Guide created successfully",
    )


@router.put("/{id}", response_model=dict)
def update_guide(
    id: str,
    request: GuideUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    guide = db.query(Guide).filter(Guide.id == id, Guide.deleted_at.is_(None)).first()
    if not guide:
        raise NotFoundException("Guide not found")
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(guide, key, value)
    db.commit()
    db.refresh(guide)
    return success_response(
        data=GuideResponse.model_validate(guide).model_dump(),
        message="Guide updated successfully",
    )


@router.delete("/{id}", response_model=dict)
def delete_guide(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    guide = db.query(Guide).filter(Guide.id == id, Guide.deleted_at.is_(None)).first()
    if not guide:
        raise NotFoundException("Guide not found")
    guide.deleted_at = datetime.now(UTC)
    db.commit()
    return success_response(message="Guide deleted successfully")
