import re
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_admin
from app.exceptions import NotFoundException
from app.models.auth import User
from app.models.people import Reviewer
from app.schemas.common import paginated_response, success_response

router = APIRouter(prefix="/reviewers", tags=["Admin - Reviewers"])


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9-]", "", value.lower().replace(" ", "-").replace("_", "-"))


class ReviewerCreate(BaseModel):
    name: str
    slug: str | None = None
    email: str | None = None
    title: str | None = None
    bio: str | None = None
    website_url: str | None = None
    social_links: dict | None = None
    credentials: list[str] | None = None
    is_active: bool = True
    status: str | None = None
    sort_order: int = 0


class ReviewerUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    email: str | None = None
    title: str | None = None
    bio: str | None = None
    website_url: str | None = None
    social_links: dict | None = None
    credentials: list[str] | None = None
    is_active: bool | None = None
    status: str | None = None
    sort_order: int | None = None


class ReviewerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    email: str | None = None
    title: str | None = None
    bio: str | None = None
    website_url: str | None = None
    social_links: dict | None = None
    credentials: list[str] | None = None
    is_active: bool
    status: str
    sort_order: int
    created_at: datetime
    updated_at: datetime


@router.get("", response_model=dict)
def list_reviewers(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    query = db.query(Reviewer).filter(Reviewer.deleted_at.is_(None))
    if is_active is not None:
        query = query.filter(Reviewer.is_active == is_active)
    total = query.count()
    items = query.order_by(Reviewer.created_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()

    data = []
    for r in items:
        d = ReviewerResponse.model_validate(r).model_dump()
        d["status"] = "active" if d["is_active"] else "inactive"
        d["reviews_count"] = len(r.calculators) if r.calculators else 0
        data.append(d)

    return paginated_response(
        data=data,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{id}", response_model=dict)
def get_reviewer(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    reviewer = db.query(Reviewer).filter(Reviewer.id == id, Reviewer.deleted_at.is_(None)).first()
    if not reviewer:
        raise NotFoundException("Reviewer not found")
    d = ReviewerResponse.model_validate(reviewer).model_dump()
    d["status"] = "active" if d["is_active"] else "inactive"
    return success_response(data=d)


@router.post("", response_model=dict)
def create_reviewer(
    request: ReviewerCreate,
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
    reviewer = Reviewer(**data)
    db.add(reviewer)
    db.commit()
    db.refresh(reviewer)
    return success_response(
        data=ReviewerResponse.model_validate(reviewer).model_dump(),
        message="Reviewer created successfully",
    )


@router.put("/{id}", response_model=dict)
def update_reviewer(
    id: str,
    request: ReviewerUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    reviewer = db.query(Reviewer).filter(Reviewer.id == id, Reviewer.deleted_at.is_(None)).first()
    if not reviewer:
        raise NotFoundException("Reviewer not found")
    update_data = request.model_dump(exclude_unset=True)
    if "status" in update_data:
        update_data["is_active"] = update_data.pop("status") == "active"
    for key, value in update_data.items():
        setattr(reviewer, key, value)
    db.commit()
    db.refresh(reviewer)
    return success_response(
        data=ReviewerResponse.model_validate(reviewer).model_dump(),
        message="Reviewer updated successfully",
    )


@router.delete("/{id}", response_model=dict)
def delete_reviewer(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    reviewer = db.query(Reviewer).filter(Reviewer.id == id, Reviewer.deleted_at.is_(None)).first()
    if not reviewer:
        raise NotFoundException("Reviewer not found")
    reviewer.deleted_at = datetime.now(UTC)
    db.commit()
    return success_response(message="Reviewer deleted successfully")
