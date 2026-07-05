from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.models.content import BlogPost, Category
from app.models.people import Author
from app.schemas.common import success_response

router = APIRouter(prefix="/blog", tags=["Public Blog"])


@router.get("", response_model=dict)
def list_public_blog_posts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    category_slug: str | None = None,
    featured: bool | None = None,
    db: Session = Depends(get_db),
):
    query = (
        db.query(BlogPost)
        .filter(
            BlogPost.deleted_at.is_(None),
            BlogPost.is_published == True,
            BlogPost.is_active == True,
        )
    )

    if category_slug:
        category = db.query(Category).filter(Category.slug == category_slug).first()
        if category:
            query = query.filter(BlogPost.category_id == category.id)

    if featured is not None:
        query = query.filter(BlogPost.is_featured == featured)

    total = query.count()
    items = (
        query.order_by(BlogPost.published_at.desc(), BlogPost.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    data = []
    for post in items:
        author = db.query(Author).filter(Author.id == post.author_id).first() if post.author_id else None
        category = db.query(Category).filter(Category.id == post.category_id).first() if post.category_id else None
        data.append({
            "id": post.id,
            "title": post.title,
            "slug": post.slug,
            "subtitle": post.subtitle,
            "excerpt": post.excerpt,
            "cover_image_url": post.cover_image_url,
            "reading_time_minutes": post.reading_time_minutes,
            "is_featured": post.is_featured,
            "is_pinned": post.is_pinned,
            "published_at": post.published_at.isoformat() if post.published_at else None,
            "author_name": author.name if author else None,
            "author_role": author.bio if author else None,
            "category_name": category.name if category else None,
            "category_slug": category.slug if category else None,
        })

    return success_response(
        data=data,
        meta={"total": total, "page": page, "per_page": per_page},
    )


@router.get("/{slug}", response_model=dict)
def get_public_blog_post(
    slug: str,
    db: Session = Depends(get_db),
):
    post = (
        db.query(BlogPost)
        .filter(
            BlogPost.slug == slug,
            BlogPost.deleted_at.is_(None),
            BlogPost.is_published == True,
            BlogPost.is_active == True,
        )
        .first()
    )
    if not post:
        from app.exceptions import NotFoundException
        raise NotFoundException("Blog post not found")

    author = db.query(Author).filter(Author.id == post.author_id).first() if post.author_id else None
    category = db.query(Category).filter(Category.id == post.category_id).first() if post.category_id else None

    return success_response(data={
        "id": post.id,
        "title": post.title,
        "slug": post.slug,
        "subtitle": post.subtitle,
        "excerpt": post.excerpt,
        "content": post.content,
        "cover_image_url": post.cover_image_url,
        "reading_time_minutes": post.reading_time_minutes,
        "is_featured": post.is_featured,
        "is_pinned": post.is_pinned,
        "published_at": post.published_at.isoformat() if post.published_at else None,
        "author_name": author.name if author else None,
        "author_role": author.bio if author else None,
        "category_name": category.name if category else None,
        "category_slug": category.slug if category else None,
    })
