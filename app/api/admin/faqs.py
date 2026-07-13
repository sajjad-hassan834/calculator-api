from datetime import UTC, datetime

from fastapi import APIRouter, Depends
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


class FAQUpdate(BaseModel):
    question: str | None = None
    answer: str | None = None
    category: str | None = None
    is_featured: bool | None = None
    is_active: bool | None = None
    status: str | None = None


class FAQResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    question: str
    answer: str
    category: str | None = None
    is_featured: bool
    is_active: bool
    status: str
    created_at: datetime
    updated_at: datetime


@router.get("")
def list_faqs(
    skip: int = 0,
    limit: int = 50,
    search: str | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    query = db.query(FAQ).filter(FAQ.deleted_at.is_(None))
    
    if search:
        query = query.filter(FAQ.question.ilike(f"%{search}%"))
        
    total = query.count()
    items = query.order_by(FAQ.created_at.desc()).offset(skip).limit(limit).all()
    
    return paginated_response(
        data=[FAQResponse.model_validate(i).model_dump() for i in items],
        total=total,
        page=(skip // limit) + 1 if limit > 0 else 1,
        per_page=limit,
    )


@router.get("/{id}")
def get_faq(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    item = db.query(FAQ).filter(
        FAQ.id == id, FAQ.deleted_at.is_(None)
    ).first()
    if not item:
        raise NotFoundException("FAQ not found")
        
    return success_response(data=FAQResponse.model_validate(item).model_dump())


@router.post("")
def create_faq(
    request: FAQCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    item = FAQ(**request.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return success_response(
        data=FAQResponse.model_validate(item).model_dump(),
        message="FAQ created successfully",
    )


@router.put("/{id}")
def update_faq(
    id: str,
    request: FAQUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    item = db.query(FAQ).filter(
        FAQ.id == id, FAQ.deleted_at.is_(None)
    ).first()
    if not item:
        raise NotFoundException("FAQ not found")
        
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
        
    db.commit()
    db.refresh(item)
    return success_response(
        data=FAQResponse.model_validate(item).model_dump(),
        message="FAQ updated successfully",
    )


@router.delete("/{id}")
def delete_faq(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    item = db.query(FAQ).filter(
        FAQ.id == id, FAQ.deleted_at.is_(None)
    ).first()
    if not item:
        raise NotFoundException("FAQ not found")
        
    item.deleted_at = datetime.now(UTC)
    db.commit()
    return success_response(message="FAQ deleted successfully")
