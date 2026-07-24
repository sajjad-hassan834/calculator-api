from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, TimestampMixin, UUIDMixin


class AIResearchTask(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "ai_research_tasks"

    topic: Mapped[str] = mapped_column(String(500), nullable=False)
    keywords: Mapped[list[str]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, in_progress, completed, failed
    priority: Mapped[int] = mapped_column(Integer, default=0)
    results: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    generated_contents: Mapped[list["AIGeneratedContent"]] = relationship(
        "AIGeneratedContent", back_populates="research_task", cascade="all, delete-orphan"
    )


class AIGeneratedContent(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "ai_generated_contents"

    research_task_id: Mapped[str | None] = mapped_column(
        ForeignKey("ai_research_tasks.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str | None] = mapped_column(String(500), unique=True, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    meta_title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    meta_description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default="draft"
    )  # draft, pending_approval, approved, published, rejected
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    research_task: Mapped["AIResearchTask"] = relationship(
        "AIResearchTask", back_populates="generated_contents"
    )
    calendar_entries: Mapped[list["ContentCalendar"]] = relationship(
        "ContentCalendar", back_populates="content", cascade="all, delete-orphan"
    )


class ContentCalendar(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "content_calendar"

    content_id: Mapped[str] = mapped_column(
        ForeignKey("ai_generated_contents.id", ondelete="CASCADE"), nullable=False
    )
    scheduled_for: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="scheduled")  # scheduled, published, failed
    publish_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    content: Mapped["AIGeneratedContent"] = relationship(
        "AIGeneratedContent", back_populates="calendar_entries"
    )


class SEOAudit(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "seo_audits"

    url: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-100
    issues: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    recommendations: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    auto_fixed: Mapped[bool] = mapped_column(Boolean, default=False)


class SEOKeyword(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "seo_keywords"

    keyword: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    search_volume: Mapped[int | None] = mapped_column(Integer, nullable=True)
    difficulty: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 0-100
    current_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    history: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)  # Track rank over time


class AIAgentLog(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "ai_agent_logs"

    agent_type: Mapped[str] = mapped_column(String(50), nullable=False)  # research, seo, content
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    cost: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # success, failed
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
