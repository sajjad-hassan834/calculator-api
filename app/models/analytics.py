from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import UTC, datetime

from app.models.base import (
    BaseModel,
    TimestampMixin,
    UUIDMixin,
)


class PageView(BaseModel):
    __tablename__ = "page_views"
    __table_args__ = {"info": {"is_analytics": True}}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    page_type: Mapped[str] = mapped_column(String(50), nullable=False)
    page_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    referrer: Mapped[str | None] = mapped_column(Text, nullable=True)
    session_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    user_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    device_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    browser: Mapped[str | None] = mapped_column(String(100), nullable=True)
    os: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(2), nullable=True)
    time_on_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=lambda: datetime.now(UTC))


class SearchHistory(BaseModel):
    __tablename__ = "search_history"
    __table_args__ = {"info": {"is_analytics": True}}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_query: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    user_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    session_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    clicked_result: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    clicked_result_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=lambda: datetime.now(UTC))


class PopularCalculator(UUIDMixin, TimestampMixin, BaseModel):
    __tablename__ = "popular_calculators"

    calculator_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("calculators.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    view_count_24h: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    view_count_7d: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    view_count_30d: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    view_count_all: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    unique_visitors_30d: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    avg_time_on_page: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    rank_24h: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rank_7d: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rank_30d: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_calculated_at: Mapped[datetime] = mapped_column(nullable=False, default=lambda: datetime.now(UTC))

    calculator = relationship("Calculator")


class KeywordPool(BaseModel):
    __tablename__ = "keyword_pool"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    keyword: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    hub_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    intent: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=lambda: datetime.now(UTC))
