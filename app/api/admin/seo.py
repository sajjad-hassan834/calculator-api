from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_admin
from app.exceptions import NotFoundException
from app.models.auth import User
from app.models.seo import SEOMetadata
from app.schemas.common import paginated_response, success_response

router = APIRouter(prefix="/seo", tags=["Admin - SEO"])


class SEOCreate(BaseModel):
    meta_title: str | None = None
    meta_description: str | None = None
    meta_keywords: list[str] | None = None
    canonical_url: str | None = None
    og_title: str | None = None
    og_description: str | None = None
    og_image_url: str | None = None
    og_type: str = "website"
    twitter_card: str = "summary_large_image"
    twitter_title: str | None = None
    twitter_description: str | None = None
    twitter_image_url: str | None = None
    json_ld: dict | None = None
    faq_schema: dict | None = None
    breadcrumb_schema: dict | None = None
    robots: str = "index, follow"
    sitemap_priority: float | None = 0.5
    sitemap_changefreq: str = "monthly"
    nofollow: bool = False
    noindex: bool = False


class SEOUpdate(BaseModel):
    meta_title: str | None = None
    meta_description: str | None = None
    meta_keywords: list[str] | None = None
    canonical_url: str | None = None
    og_title: str | None = None
    og_description: str | None = None
    og_image_url: str | None = None
    og_type: str | None = None
    twitter_card: str | None = None
    twitter_title: str | None = None
    twitter_description: str | None = None
    twitter_image_url: str | None = None
    json_ld: dict | None = None
    faq_schema: dict | None = None
    breadcrumb_schema: dict | None = None
    robots: str | None = None
    sitemap_priority: float | None = None
    sitemap_changefreq: str | None = None
    nofollow: bool | None = None
    noindex: bool | None = None


class SEOResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    meta_title: str | None = None
    meta_description: str | None = None
    meta_keywords: list[str] | None = None
    canonical_url: str | None = None
    og_title: str | None = None
    og_description: str | None = None
    og_image_url: str | None = None
    og_type: str | None = None
    twitter_card: str | None = None
    twitter_title: str | None = None
    twitter_description: str | None = None
    twitter_image_url: str | None = None
    json_ld: dict | None = None
    faq_schema: dict | None = None
    breadcrumb_schema: dict | None = None
    robots: str | None = None
    sitemap_priority: float | None = None
    sitemap_changefreq: str | None = None
    nofollow: bool
    noindex: bool
    created_at: datetime
    updated_at: datetime


@router.get("", response_model=dict)
def list_seo_metadata(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    query = db.query(SEOMetadata)
    total = query.count()
    items = query.order_by(SEOMetadata.created_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()
    return paginated_response(
        data=[SEOResponse.model_validate(s).model_dump() for s in items],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{id}", response_model=dict)
def get_seo_metadata(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    seo = db.query(SEOMetadata).filter(SEOMetadata.id == id).first()
    if not seo:
        raise NotFoundException("SEO metadata not found")
    return success_response(data=SEOResponse.model_validate(seo).model_dump())


@router.post("", response_model=dict)
def create_seo_metadata(
    request: SEOCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    seo = SEOMetadata(**request.model_dump())
    db.add(seo)
    db.commit()
    db.refresh(seo)
    return success_response(
        data=SEOResponse.model_validate(seo).model_dump(),
        message="SEO metadata created successfully",
    )


@router.put("/{id}", response_model=dict)
def update_seo_metadata(
    id: str,
    request: SEOUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    seo = db.query(SEOMetadata).filter(SEOMetadata.id == id).first()
    if not seo:
        raise NotFoundException("SEO metadata not found")
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(seo, key, value)
    db.commit()
    db.refresh(seo)
    return success_response(
        data=SEOResponse.model_validate(seo).model_dump(),
        message="SEO metadata updated successfully",
    )


@router.delete("/{id}", response_model=dict)
def delete_seo_metadata(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    seo = db.query(SEOMetadata).filter(SEOMetadata.id == id).first()
    if not seo:
        raise NotFoundException("SEO metadata not found")
    db.delete(seo)
    db.commit()
    return success_response(message="SEO metadata deleted successfully")
