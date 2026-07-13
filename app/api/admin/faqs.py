from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_admin
from app.exceptions import NotFoundException
from app.models.auth import User
from app.models.content import FAQ
from app.schemas.common import paginated_response, success_response

router = APIRouter(prefix="/faqs", tags=["Admin - FAQs"])


class FAQCreate(BaseModel):
    question: str
    answer: str
    category: str | None = None
    is_featured: bool = False
    is_active: bool = True
    status: str = "published"
    sort_order: int = 0


class FAQUpdate(BaseModel):
    question: str | None = None
    answer: str | None = None
    category: str | None = None
    is_featured: bool | None = None
    is_active: bool | None = None
    status: str | None = None
    sort_order: int | None = None


class FAQResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    question: str
    answer: str
    category: str | None = None
    is_featured: bool
    is_active: bool
    status: str
    sort_order: int
    created_at: datetime
    updated_at: datetime


@router.get("", response_model=dict)
def list_faqs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str | None = None,
    search: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    query = db.query(FAQ).filter(FAQ.deleted_at.is_(None))
    if status is not None:
        query = query.filter(FAQ.status == status)
    if category:
        query = query.filter(FAQ.category == category)
    if search:
        query = query.filter(FAQ.question.ilike(f"%{search}%"))
    total = query.count()
    items = query.order_by(FAQ.sort_order.asc(), FAQ.created_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()

    data = [FAQResponse.model_validate(f).model_dump() for f in items]
    return paginated_response(data=data, total=total, page=page, per_page=per_page)


@router.get("/{id}", response_model=dict)
def get_faq(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    faq = db.query(FAQ).filter(FAQ.id == id, FAQ.deleted_at.is_(None)).first()
    if not faq:
        raise NotFoundException("FAQ not found")
    return success_response(data=FAQResponse.model_validate(faq).model_dump())


@router.post("", response_model=dict)
def create_faq(
    request: FAQCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    faq = FAQ(**request.model_dump())
    db.add(faq)
    db.commit()
    db.refresh(faq)
    return success_response(
        data=FAQResponse.model_validate(faq).model_dump(),
        message="FAQ created successfully",
    )


@router.put("/{id}", response_model=dict)
def update_faq(
    id: str,
    request: FAQUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    faq = db.query(FAQ).filter(FAQ.id == id, FAQ.deleted_at.is_(None)).first()
    if not faq:
        raise NotFoundException("FAQ not found")
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(faq, key, value)
    db.commit()
    db.refresh(faq)
    return success_response(
        data=FAQResponse.model_validate(faq).model_dump(),
        message="FAQ updated successfully",
    )


@router.delete("/{id}", response_model=dict)
def delete_faq(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    faq = db.query(FAQ).filter(FAQ.id == id, FAQ.deleted_at.is_(None)).first()
    if not faq:
        raise NotFoundException("FAQ not found")
    faq.deleted_at = datetime.now(UTC)
    db.commit()
    return success_response(message="FAQ deleted successfully")
