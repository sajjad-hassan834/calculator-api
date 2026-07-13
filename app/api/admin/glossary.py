from datetime import UTC, datetime

from fastapi import APIRouter, Depends
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
    seo_metadata_id: str | None = None
    is_active: bool = True
    status: str = "published"


class GlossaryTermUpdate(BaseModel):
    term: str | None = None
    slug: str | None = None
    definition: str | None = None
    category: str | None = None
    related_terms: list[str] | None = None
    seo_metadata_id: str | None = None
    is_active: bool | None = None
    status: str | None = None


class GlossaryTermResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    term: str
    slug: str
    definition: str
    category: str | None = None
    related_terms: list[str] | None = None
    seo_metadata_id: str | None = None
    is_active: bool
    status: str
    created_at: datetime
    updated_at: datetime


@router.get("")
def list_glossary_terms(
    skip: int = 0,
    limit: int = 50,
    search: str | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    query = db.query(GlossaryTerm).filter(GlossaryTerm.deleted_at.is_(None))
    
    if search:
        query = query.filter(GlossaryTerm.term.ilike(f"%{search}%"))
        
    total = query.count()
    items = query.order_by(GlossaryTerm.created_at.desc()).offset(skip).limit(limit).all()
    
    return paginated_response(
        data=[GlossaryTermResponse.model_validate(i).model_dump() for i in items],
        total=total,
        page=(skip // limit) + 1 if limit > 0 else 1,
        per_page=limit,
    )


@router.get("/{id}")
def get_glossary_term(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    item = db.query(GlossaryTerm).filter(
        GlossaryTerm.id == id, GlossaryTerm.deleted_at.is_(None)
    ).first()
    if not item:
        raise NotFoundException("Glossary term not found")
        
    return success_response(data=GlossaryTermResponse.model_validate(item).model_dump())


@router.post("")
def create_glossary_term(
    request: GlossaryTermCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    item = GlossaryTerm(**request.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return success_response(
        data=GlossaryTermResponse.model_validate(item).model_dump(),
        message="Glossary term created successfully",
    )


@router.put("/{id}")
def update_glossary_term(
    id: str,
    request: GlossaryTermUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    item = db.query(GlossaryTerm).filter(
        GlossaryTerm.id == id, GlossaryTerm.deleted_at.is_(None)
    ).first()
    if not item:
        raise NotFoundException("Glossary term not found")
        
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
        
    db.commit()
    db.refresh(item)
    return success_response(
        data=GlossaryTermResponse.model_validate(item).model_dump(),
        message="Glossary term updated successfully",
    )


@router.delete("/{id}")
def delete_glossary_term(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    item = db.query(GlossaryTerm).filter(
        GlossaryTerm.id == id, GlossaryTerm.deleted_at.is_(None)
    ).first()
    if not item:
        raise NotFoundException("Glossary term not found")
        
    item.deleted_at = datetime.now(UTC)
    db.commit()
    return success_response(message="Glossary term deleted successfully")
