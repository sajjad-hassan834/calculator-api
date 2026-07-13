from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_admin
from app.exceptions import NotFoundException
from app.models.auth import User
from app.models.content import GlossaryTerm
from app.schemas.common import paginated_response, success_response

router = APIRouter(prefix="/glossary", tags=["Admin - Glossary"])


class GlossaryTermCreate(BaseModel):
    term: str
    slug: str
    definition: str
    category: str | None = None
    related_terms: list[str] | None = None
    is_active: bool = True
    status: str = "published"
    sort_order: int = 0


class GlossaryTermUpdate(BaseModel):
    term: str | None = None
    slug: str | None = None
    definition: str | None = None
    category: str | None = None
    related_terms: list[str] | None = None
    is_active: bool | None = None
    status: str | None = None
    sort_order: int | None = None


class GlossaryTermResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    term: str
    slug: str
    definition: str
    category: str | None = None
    related_terms: list[str] | None = None
    is_active: bool
    status: str
    sort_order: int
    created_at: datetime
    updated_at: datetime


@router.get("", response_model=dict)
def list_glossary_terms(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    query = db.query(GlossaryTerm).filter(GlossaryTerm.deleted_at.is_(None))
    if status is not None:
        query = query.filter(GlossaryTerm.status == status)
    if search:
        query = query.filter(GlossaryTerm.term.ilike(f"%{search}%"))
    total = query.count()
    items = query.order_by(GlossaryTerm.sort_order.asc(), GlossaryTerm.term.asc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()

    data = [GlossaryTermResponse.model_validate(t).model_dump() for t in items]
    return paginated_response(data=data, total=total, page=page, per_page=per_page)


@router.get("/{id}", response_model=dict)
def get_glossary_term(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    term = db.query(GlossaryTerm).filter(GlossaryTerm.id == id, GlossaryTerm.deleted_at.is_(None)).first()
    if not term:
        raise NotFoundException("Glossary term not found")
    return success_response(data=GlossaryTermResponse.model_validate(term).model_dump())


@router.post("", response_model=dict)
def create_glossary_term(
    request: GlossaryTermCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    term = GlossaryTerm(**request.model_dump())
    db.add(term)
    db.commit()
    db.refresh(term)
    return success_response(
        data=GlossaryTermResponse.model_validate(term).model_dump(),
        message="Glossary term created successfully",
    )


@router.put("/{id}", response_model=dict)
def update_glossary_term(
    id: str,
    request: GlossaryTermUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    term = db.query(GlossaryTerm).filter(GlossaryTerm.id == id, GlossaryTerm.deleted_at.is_(None)).first()
    if not term:
        raise NotFoundException("Glossary term not found")
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(term, key, value)
    db.commit()
    db.refresh(term)
    return success_response(
        data=GlossaryTermResponse.model_validate(term).model_dump(),
        message="Glossary term updated successfully",
    )


@router.delete("/{id}", response_model=dict)
def delete_glossary_term(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    term = db.query(GlossaryTerm).filter(GlossaryTerm.id == id, GlossaryTerm.deleted_at.is_(None)).first()
    if not term:
        raise NotFoundException("Glossary term not found")
    term.deleted_at = datetime.now(UTC)
    db.commit()
    return success_response(message="Glossary term deleted successfully")
