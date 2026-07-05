from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    AuditMixin,
    BaseModel,
    SlugMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)


class SEOMetadata(UUIDMixin, TimestampMixin, BaseModel):
    __tablename__ = "seo_metadata"

    meta_title: Mapped[str | None] = mapped_column(String(70), nullable=True)
    meta_description: Mapped[str | None] = mapped_column(String(160), nullable=True)
    meta_keywords: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)
    canonical_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    og_title: Mapped[str | None] = mapped_column(String(70), nullable=True)
    og_description: Mapped[str | None] = mapped_column(String(160), nullable=True)
    og_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    og_type: Mapped[str] = mapped_column(String(50), default="website", nullable=True)
    twitter_card: Mapped[str] = mapped_column(String(50), default="summary_large_image", nullable=True)
    twitter_title: Mapped[str | None] = mapped_column(String(70), nullable=True)
    twitter_description: Mapped[str | None] = mapped_column(String(160), nullable=True)
    twitter_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    json_ld: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    faq_schema: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    breadcrumb_schema: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    robots: Mapped[str] = mapped_column(String(255), default="index, follow", nullable=True)
    sitemap_priority: Mapped[float | None] = mapped_column(Numeric(2, 1), default=0.5, nullable=True)
    sitemap_changefreq: Mapped[str] = mapped_column(String(20), default="monthly", nullable=True)
    nofollow: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    noindex: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Redirect(UUIDMixin, TimestampMixin, AuditMixin, BaseModel):
    __tablename__ = "redirects"

    source_url: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    target_url: Mapped[str] = mapped_column(Text, nullable=False)
    redirect_type: Mapped[int] = mapped_column(Integer, default=301, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    hit_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    last_hit_at: Mapped[str | None] = mapped_column(nullable=True)


class Sitemap(UUIDMixin, TimestampMixin, BaseModel):
    __tablename__ = "sitemaps"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sitemap_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entries: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    generated_at: Mapped[str | None] = mapped_column(nullable=True)
    file_url: Mapped[str | None] = mapped_column(Text, nullable=True)


class CustomPage(UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, SlugMixin, BaseModel):
    __tablename__ = "custom_pages"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    template: Mapped[str] = mapped_column(String(100), default="default", nullable=True)
    seo_metadata_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("seo_metadata.id", ondelete="SET NULL"), nullable=True
    )
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")

    seo_metadata = relationship("SEOMetadata", lazy="joined")
