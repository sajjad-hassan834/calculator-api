import re
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_admin
from app.exceptions import NotFoundException
from app.models.auth import User
from app.models.people import Author
from app.schemas.common import paginated_response, success_response

router = APIRouter(prefix="/authors", tags=["Admin - Authors"])


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9-]", "", value.lower().replace(" ", "-").replace("_", "-"))


class AuthorCreate(BaseModel):
    name: str
    slug: str | None = None
    email: str | None = None
    bio: str | None = None
    website_url: str | None = None
    social_links: dict | None = None
    expertise_areas: list[str] | None = None
    is_active: bool = True
    status: str | None = None
    sort_order: int = 0


class AuthorUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    email: str | None = None
    bio: str | None = None
    website_url: str | None = None
    social_links: dict | None = None
    expertise_areas: list[str] | None = None
    is_active: bool | None = None
    status: str | None = None
    sort_order: int | None = None


class AuthorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    email: str | None = None
    bio: str | None = None
    website_url: str | None = None
    social_links: dict | None = None
    expertise_areas: list[str] | None = None
    is_active: bool
    status: str
    sort_order: int
    created_at: datetime
    updated_at: datetime


@router.get("", response_model=dict)
def list_authors(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    query = db.query(Author).filter(Author.deleted_at.is_(None))
    if is_active is not None:
        query = query.filter(Author.is_active == is_active)
    total = query.count()
    items = query.order_by(Author.created_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()

    data = []
    for a in items:
        d = AuthorResponse.model_validate(a).model_dump()
        d["status"] = "active" if d["is_active"] else "inactive"
        d["articles_count"] = len(a.calculators) + len(a.blog_posts) + len(a.guides) if a.calculators and a.blog_posts and a.guides else 0
        calc_reviews = len(a.calculators) if a.calculators else 0
        d["calc_reviews_count"] = calc_reviews
        data.append(d)

    return paginated_response(
        data=data,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{id}", response_model=dict)
def get_author(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    author = db.query(Author).filter(Author.id == id, Author.deleted_at.is_(None)).first()
    if not author:
        raise NotFoundException("Author not found")
    d = AuthorResponse.model_validate(author).model_dump()
    d["status"] = "active" if d["is_active"] else "inactive"
    return success_response(data=d)


@router.post("", response_model=dict)
def create_author(
    request: AuthorCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    data = request.model_dump(exclude_unset=True)
    if not data.get("slug"):
        data["slug"] = _slugify(data["name"])
    if "status" in data:
        data["is_active"] = data.pop("status") == "active"
    if "is_active" in data and isinstance(data.get("is_active"), str):
        data["is_active"] = data["is_active"] == "active"
    author = Author(**data)
    db.add(author)
    db.commit()
    db.refresh(author)
    return success_response(
        data=AuthorResponse.model_validate(author).model_dump(),
        message="Author created successfully",
    )


@router.put("/{id}", response_model=dict)
def update_author(
    id: str,
    request: AuthorUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    author = db.query(Author).filter(Author.id == id, Author.deleted_at.is_(None)).first()
    if not author:
        raise NotFoundException("Author not found")
    update_data = request.model_dump(exclude_unset=True)
    if "status" in update_data:
        update_data["is_active"] = update_data.pop("status") == "active"
    for key, value in update_data.items():
        setattr(author, key, value)
    db.commit()
    db.refresh(author)
    return success_response(
        data=AuthorResponse.model_validate(author).model_dump(),
        message="Author updated successfully",
    )


@router.delete("/{id}", response_model=dict)
def delete_author(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    author = db.query(Author).filter(Author.id == id, Author.deleted_at.is_(None)).first()
    if not author:
        raise NotFoundException("Author not found")
    author.deleted_at = datetime.now(UTC)
    db.commit()
    return success_response(message="Author deleted successfully")
