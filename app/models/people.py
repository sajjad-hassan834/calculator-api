from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    AuditMixin,
    BaseModel,
    SlugMixin,
    SoftDeleteMixin,
    SortOrderMixin,
    TimestampMixin,
    UUIDMixin,
)


class Author(UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, SortOrderMixin, SlugMixin, BaseModel):
    __tablename__ = "authors"

    user_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, unique=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_media_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("media.id", ondelete="SET NULL"), nullable=True
    )
    website_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    social_links: Mapped[dict | None] = mapped_column(JSONB, default=dict, nullable=True)
    designation: Mapped[str | None] = mapped_column(String(255), nullable=True)
    credentials: Mapped[str | None] = mapped_column(String(255), nullable=True)
    expertise_areas: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    calculators = relationship("Calculator", back_populates="author", lazy="selectin")
    blog_posts = relationship("BlogPost", back_populates="author", lazy="selectin")
    guides = relationship("Guide", back_populates="author", lazy="selectin")


class Reviewer(UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, SortOrderMixin, SlugMixin, BaseModel):
    __tablename__ = "reviewers"

    user_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, unique=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_media_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("media.id", ondelete="SET NULL"), nullable=True
    )
    website_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    social_links: Mapped[dict | None] = mapped_column(JSONB, default=dict, nullable=True)
    credentials: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    calculators = relationship("Calculator", back_populates="reviewer", lazy="selectin")
    blog_posts = relationship("BlogPost", back_populates="reviewer", lazy="selectin")
    guides = relationship("Guide", back_populates="reviewer", lazy="selectin")
