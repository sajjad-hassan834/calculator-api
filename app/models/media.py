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
    BaseModel,
    SlugMixin,
    SoftDeleteMixin,
    SortOrderMixin,
    TimestampMixin,
    UUIDMixin,
)


class MediaFolder(UUIDMixin, TimestampMixin, SoftDeleteMixin, SortOrderMixin, BaseModel):
    __tablename__ = "media_folders"

    parent_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("media_folders.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    parent = relationship("MediaFolder", remote_side="MediaFolder.id", back_populates="children")
    children = relationship("MediaFolder", back_populates="parent", lazy="selectin")
    media = relationship("Media", back_populates="folder", lazy="selectin", cascade="all, delete-orphan")


class Media(UUIDMixin, TimestampMixin, SoftDeleteMixin, BaseModel):
    __tablename__ = "media"

    folder_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("media_folders.id", ondelete="SET NULL"), nullable=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_extension: Mapped[str] = mapped_column(String(20), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_bucket: Mapped[str] = mapped_column(String(100), nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    public_url: Mapped[str] = mapped_column(Text, nullable=False)
    alt_text: Mapped[str | None] = mapped_column(String(500), nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_type: Mapped[str] = mapped_column(String(50), nullable=False)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    dominant_color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    blur_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    uploaded_by: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    folder = relationship("MediaFolder", back_populates="media")


class CalculatorMedia(UUIDMixin, TimestampMixin, SortOrderMixin, BaseModel):
    __tablename__ = "calculator_media"

    calculator_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("calculators.id", ondelete="CASCADE"), nullable=False
    )
    media_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("media.id", ondelete="CASCADE"), nullable=False
    )
    media_type: Mapped[str] = mapped_column(String(50), nullable=False, default="image")

    __table_args__ = (
        UniqueConstraint("calculator_id", "media_id", "media_type", name="uq_calculator_media"),
    )

    calculator = relationship("Calculator", back_populates="media")
    media = relationship("Media")


class BlogMedia(UUIDMixin, TimestampMixin, SortOrderMixin, BaseModel):
    __tablename__ = "blog_media"

    blog_post_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("blog_posts.id", ondelete="CASCADE"), nullable=False
    )
    media_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("media.id", ondelete="CASCADE"), nullable=False
    )
    media_type: Mapped[str] = mapped_column(String(50), nullable=False, default="image")

    __table_args__ = (
        UniqueConstraint("blog_post_id", "media_id", name="uq_blog_media"),
    )

    blog_post = relationship("BlogPost", back_populates="media")
    media = relationship("Media")


class GuideMedia(UUIDMixin, TimestampMixin, SortOrderMixin, BaseModel):
    __tablename__ = "guide_media"

    guide_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("guides.id", ondelete="CASCADE"), nullable=False
    )
    media_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("media.id", ondelete="CASCADE"), nullable=False
    )
    media_type: Mapped[str] = mapped_column(String(50), nullable=False, default="image")

    __table_args__ = (
        UniqueConstraint("guide_id", "media_id", name="uq_guide_media"),
    )

    guide = relationship("Guide", back_populates="media")
    media = relationship("Media")
