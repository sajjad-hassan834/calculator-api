from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.content import Guide, Category
from app.models.people import Author
from app.schemas.common import success_response

router = APIRouter(prefix="/guides", tags=["Public Guides"])


@router.get("", response_model=dict)
def list_public_guides(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    category_slug: str | None = None,
    featured: bool | None = None,
    db: Session = Depends(get_db),
):
    query = (
        db.query(Guide)
        .filter(
            Guide.deleted_at.is_(None),
            Guide.is_published == True,
            Guide.is_active == True,
        )
    )

    if category_slug:
        category = db.query(Category).filter(Category.slug == category_slug).first()
        if category:
            query = query.filter(Guide.category_id == category.id)

    if featured is not None:
        query = query.filter(Guide.is_featured == featured)

    total = query.count()
    items = (
        query.order_by(Guide.published_at.desc(), Guide.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    data = []
    for guide in items:
        author = db.query(Author).filter(Author.id == guide.author_id).first() if guide.author_id else None
        category = db.query(Category).filter(Category.id == guide.category_id).first() if guide.category_id else None
        data.append({
            "id": guide.id,
            "title": guide.title,
            "slug": guide.slug,
            "subtitle": guide.subtitle,
            "excerpt": guide.excerpt,
            "cover_image_url": guide.cover_image_url,
            "reading_time_minutes": guide.reading_time_minutes,
            "difficulty_level": guide.difficulty_level,
            "is_featured": guide.is_featured,
            "published_at": guide.published_at.isoformat() if guide.published_at else None,
            "author_name": author.name if author else None,
            "category_name": category.name if category else None,
            "category_slug": category.slug if category else None,
        })

    return success_response(
        data=data,
        meta={"total": total, "page": page, "per_page": per_page},
    )


@router.get("/{slug}", response_model=dict)
def get_public_guide(
    slug: str,
    db: Session = Depends(get_db),
):
    guide = (
        db.query(Guide)
        .filter(
            Guide.slug == slug,
            Guide.deleted_at.is_(None),
            Guide.is_published == True,
            Guide.is_active == True,
        )
        .first()
    )
    if not guide:
        from app.exceptions import NotFoundException
        raise NotFoundException("Guide not found")

    author = db.query(Author).filter(Author.id == guide.author_id).first() if guide.author_id else None
    category = db.query(Category).filter(Category.id == guide.category_id).first() if guide.category_id else None

    return success_response(data={
        "id": guide.id,
        "title": guide.title,
        "slug": guide.slug,
        "subtitle": guide.subtitle,
        "excerpt": guide.excerpt,
        "content": guide.content,
        "cover_image_url": guide.cover_image_url,
        "reading_time_minutes": guide.reading_time_minutes,
        "difficulty_level": guide.difficulty_level,
        "is_featured": guide.is_featured,
        "published_at": guide.published_at.isoformat() if guide.published_at else None,
        "author_name": author.name if author else None,
        "category_name": category.name if category else None,
        "category_slug": category.slug if category else None,
    })
