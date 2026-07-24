from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_admin
from app.exceptions import NotFoundException
from app.models.auth import User
from app.models.content import BlogPost
from app.schemas.common import paginated_response, success_response

router = APIRouter(prefix="/blog", tags=["Admin - Blog"])


class BlogPostCreate(BaseModel):
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
    is_featured: bool = False
    is_pinned: bool = False
    is_active: bool = True
    is_published: bool = False
    status: str = "draft"
    published_at: datetime | None = None
    scheduled_at: datetime | None = None


class BlogPostUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    category_id: str | None = None
    author_id: str | None = None
    reviewer_id: str | None = None
    subtitle: str | None = None
    excerpt: str | None = None
    content: str | None = None
    cover_image_url: str | None = None
    reading_time_minutes: int | None = None
    is_featured: bool | None = None
    is_pinned: bool | None = None
    is_active: bool | None = None
    is_published: bool | None = None
    status: str | None = None
    published_at: datetime | None = None
    scheduled_at: datetime | None = None


class BlogPostResponse(BaseModel):
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
    is_featured: bool
    is_pinned: bool
    is_active: bool
    is_published: bool
    status: str
    view_count: int = 0
    seo_score: int = 0
    published_at: datetime | None = None
    scheduled_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


@router.get("", response_model=dict)
def list_blog_posts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str | None = None,
    category_id: str | None = None,
    author_id: str | None = None,
    is_published: bool | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    query = db.query(BlogPost).filter(BlogPost.deleted_at.is_(None))
    if status:
        query = query.filter(BlogPost.status == status)
    if category_id:
        query = query.filter(BlogPost.category_id == category_id)
    if author_id:
        query = query.filter(BlogPost.author_id == author_id)
    if is_published is not None:
        query = query.filter(BlogPost.is_published == is_published)
    total = query.count()
    items = query.order_by(BlogPost.created_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()

    from app.models.seo import SEOMetadata

    data = []
    for p in items:
        d = BlogPostResponse.model_validate(p).model_dump()
        if p.seo_metadata_id:
            seo = db.query(SEOMetadata).filter(SEOMetadata.id == p.seo_metadata_id).first()
            d["seo_score"] = seo.seo_score if seo else 0
        data.append(d)

    return paginated_response(
        data=data,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{id}", response_model=dict)
def get_blog_post(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    post = db.query(BlogPost).filter(BlogPost.id == id, BlogPost.deleted_at.is_(None)).first()
    if not post:
        raise NotFoundException("Blog post not found")
    from app.models.seo import SEOMetadata
    d = BlogPostResponse.model_validate(post).model_dump()
    if post.seo_metadata_id:
        seo = db.query(SEOMetadata).filter(SEOMetadata.id == post.seo_metadata_id).first()
        d["seo_score"] = seo.seo_score if seo else 0
    return success_response(data=d)


@router.post("", response_model=dict)
def create_blog_post(
    request: BlogPostCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    data = request.model_dump()
    if data.get("slug"):
        base_slug = data["slug"]
        slug = base_slug
        counter = 1
        while db.query(BlogPost).filter(BlogPost.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        data["slug"] = slug

    if data.get("is_published") and not data.get("published_at"):
        data["published_at"] = datetime.now(UTC)
    post = BlogPost(**data)
    db.add(post)
    db.commit()
    db.refresh(post)
    return success_response(
        data=BlogPostResponse.model_validate(post).model_dump(),
        message="Blog post created successfully",
    )


@router.put("/{id}", response_model=dict)
def update_blog_post(
    id: str,
    request: BlogPostUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    post = db.query(BlogPost).filter(BlogPost.id == id, BlogPost.deleted_at.is_(None)).first()
    if not post:
        raise NotFoundException("Blog post not found")
    update_data = request.model_dump(exclude_unset=True)
    if update_data.get("slug"):
        base_slug = update_data["slug"]
        slug = base_slug
        counter = 1
        while db.query(BlogPost).filter(BlogPost.slug == slug, BlogPost.id != post.id).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        update_data["slug"] = slug

    is_publishing = update_data.get("is_published") is True and not post.is_published
    if is_publishing and not update_data.get("published_at"):
        update_data["published_at"] = datetime.now(UTC)
    for key, value in update_data.items():
        setattr(post, key, value)
    db.commit()
    db.refresh(post)
    return success_response(
        data=BlogPostResponse.model_validate(post).model_dump(),
        message="Blog post updated successfully",
    )


@router.delete("/{id}", response_model=dict)
def delete_blog_post(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    post = db.query(BlogPost).filter(BlogPost.id == id, BlogPost.deleted_at.is_(None)).first()
    if not post:
        raise NotFoundException("Blog post not found")
    post.deleted_at = datetime.now(UTC)
    db.commit()
    return success_response(message="Blog post deleted successfully")
