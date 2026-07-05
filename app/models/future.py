from sqlalchemy import (
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
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)


class Bookmark(UUIDMixin, TimestampMixin, BaseModel):
    __tablename__ = "bookmarks"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    calculator_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("calculators.id", ondelete="CASCADE"), nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "calculator_id", name="uq_bookmarks"),
    )


class SavedCalculation(UUIDMixin, TimestampMixin, SoftDeleteMixin, BaseModel):
    __tablename__ = "saved_calculations"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    calculator_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("calculators.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    input_values: Mapped[dict] = mapped_column(JSONB, nullable=False)
    output_values: Mapped[dict] = mapped_column(JSONB, nullable=False)
    share_token: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True)
    is_shared: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Notification(UUIDMixin, TimestampMixin, BaseModel):
    __tablename__ = "notifications"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[str | None] = mapped_column(nullable=True)


class AIExplanation(UUIDMixin, TimestampMixin, BaseModel):
    __tablename__ = "ai_explanations"

    calculator_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("calculators.id", ondelete="CASCADE"), nullable=False
    )
    explanation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    generated_by: Mapped[str] = mapped_column(String(50), nullable=False)
    model_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    calculator = relationship("Calculator")
