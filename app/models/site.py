from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    AuditMixin,
    BaseModel,
    SoftDeleteMixin,
    SortOrderMixin,
    StatusMixin,
    TimestampMixin,
    UUIDMixin,
)


class HomepageSection(UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, SortOrderMixin, BaseModel):
    __tablename__ = "homepage_sections"

    section_key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subtitle: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    section_type: Mapped[str] = mapped_column(String(50), nullable=False)
    config: Mapped[dict | None] = mapped_column(JSONB, default=dict, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class NavigationItem(UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, SortOrderMixin, BaseModel):
    __tablename__ = "navigation_items"

    parent_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("navigation_items.id", ondelete="SET NULL"), nullable=True
    )
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    page_reference_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    page_reference_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), nullable=True
    )
    icon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    target: Mapped[str] = mapped_column(String(20), default="_self", nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_mega_menu: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mega_menu_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    parent = relationship("NavigationItem", remote_side="NavigationItem.id", back_populates="children")
    children = relationship("NavigationItem", back_populates="parent", lazy="selectin")


class FooterColumn(UUIDMixin, TimestampMixin, SortOrderMixin, BaseModel):
    __tablename__ = "footer_columns"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    links = relationship("FooterLink", back_populates="column", lazy="selectin", cascade="all, delete-orphan")


class FooterLink(UUIDMixin, TimestampMixin, SortOrderMixin, BaseModel):
    __tablename__ = "footer_links"

    footer_column_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("footer_columns.id", ondelete="CASCADE"), nullable=False
    )
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    column = relationship("FooterColumn", back_populates="links")


class Advertisement(UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, BaseModel):
    __tablename__ = "advertisements"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    ad_type: Mapped[str] = mapped_column(String(50), nullable=False)
    placement: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    link_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_blank: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_responsive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    start_date: Mapped[str | None] = mapped_column(nullable=True)
    end_date: Mapped[str | None] = mapped_column(nullable=True)
    max_impressions: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    max_clicks: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    current_impressions: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    current_clicks: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Testimonial(UUIDMixin, TimestampMixin, SoftDeleteMixin, SortOrderMixin, BaseModel):
    __tablename__ = "testimonials"

    author_name: Mapped[str] = mapped_column(String(255), nullable=False)
    author_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author_avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class NewsletterSubscriber(UUIDMixin, TimestampMixin, BaseModel):
    __tablename__ = "newsletter_subscribers"

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verified_at: Mapped[str | None] = mapped_column(nullable=True)
    subscribed_at: Mapped[str] = mapped_column(nullable=False)
    unsubscribed_at: Mapped[str | None] = mapped_column(nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class SiteSetting(UUIDMixin, TimestampMixin, AuditMixin, BaseModel):
    __tablename__ = "site_settings"

    key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    group: Mapped[str] = mapped_column(String(100), default="general", nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
