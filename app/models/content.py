from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
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
    SortOrderMixin,
    StatusMixin,
    TimestampMixin,
    UUIDMixin,
)


class Category(UUIDMixin, TimestampMixin, SoftDeleteMixin, SortOrderMixin, StatusMixin, BaseModel):
    __tablename__ = "categories"

    parent_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(500), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    color_hex: Mapped[str | None] = mapped_column(String(7), nullable=True)
    seo_metadata_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("seo_metadata.id", ondelete="SET NULL"), nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    parent = relationship("Category", remote_side="Category.id", back_populates="children")
    children = relationship("Category", back_populates="parent", lazy="selectin")
    seo_metadata = relationship("SEOMetadata", lazy="joined")
    calculators = relationship("Calculator", back_populates="category", lazy="selectin")
    blog_posts = relationship("BlogPost", back_populates="category", lazy="selectin")
    guides = relationship("Guide", back_populates="category", lazy="selectin")


class Calculator(UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, SortOrderMixin, SlugMixin, BaseModel):
    __tablename__ = "calculators"

    category_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    author_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("authors.id", ondelete="SET NULL"), nullable=True
    )
    reviewer_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("reviewers.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    short_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    keywords: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)
    calculator_type: Mapped[str] = mapped_column(String(100), nullable=False)
    engine_type: Mapped[str] = mapped_column(String(100), nullable=False, default="formula")
    engine_config: Mapped[dict | None] = mapped_column(JSONB, default=dict, nullable=True)
    input_schema: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    output_schema: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    formula_expression: Mapped[str | None] = mapped_column(Text, nullable=True)
    default_values: Mapped[dict | None] = mapped_column(JSONB, default=dict, nullable=True)
    validation_rules: Mapped[dict | None] = mapped_column(JSONB, default=dict, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=True)
    country: Mapped[str] = mapped_column(String(2), default="US", nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_popular: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_calculator: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    published_at: Mapped[datetime | None] = mapped_column(nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(nullable=True)
    view_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    seo_metadata_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("seo_metadata.id", ondelete="SET NULL"), nullable=True
    )

    __table_args__ = (
        CheckConstraint("status IN ('draft', 'published', 'archived', 'scheduled')", name="ck_calculators_status"),
        Index("idx_calculators_category_published", "category_id", "is_published"),
    )

    category = relationship("Category", back_populates="calculators")
    author = relationship("Author", back_populates="calculators")
    reviewer = relationship("Reviewer", back_populates="calculators")
    seo_metadata = relationship("SEOMetadata", lazy="joined")
    inputs = relationship("CalculatorInput", back_populates="calculator", lazy="selectin", cascade="all, delete-orphan")
    outputs = relationship("CalculatorOutput", back_populates="calculator", lazy="selectin", cascade="all, delete-orphan")
    formulas = relationship("CalculatorFormula", back_populates="calculator", lazy="selectin", cascade="all, delete-orphan")
    faqs = relationship("CalculatorFAQ", back_populates="calculator", lazy="selectin", cascade="all, delete-orphan")
    examples = relationship("CalculatorExample", back_populates="calculator", lazy="selectin", cascade="all, delete-orphan")
    references = relationship("CalculatorReference", back_populates="calculator", lazy="selectin", cascade="all, delete-orphan")
    charts = relationship("CalculatorChart", back_populates="calculator", lazy="selectin", cascade="all, delete-orphan")
    sections = relationship("CalculatorSection", back_populates="calculator", lazy="selectin", cascade="all, delete-orphan")
    related_calculators = relationship(
        "RelatedCalculator",
        back_populates="calculator",
        lazy="selectin",
        cascade="all, delete-orphan",
        foreign_keys="RelatedCalculator.calculator_id",
    )
    media = relationship("CalculatorMedia", back_populates="calculator", lazy="selectin", cascade="all, delete-orphan")


class CalculatorInput(UUIDMixin, TimestampMixin, SortOrderMixin, BaseModel):
    __tablename__ = "calculator_inputs"

    calculator_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("calculators.id", ondelete="CASCADE"), nullable=False
    )
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    input_type: Mapped[str] = mapped_column(String(50), nullable=False)
    data_type: Mapped[str] = mapped_column(String(50), nullable=False, default="number")
    placeholder: Mapped[str | None] = mapped_column(String(255), nullable=True)
    help_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    suffix: Mapped[str | None] = mapped_column(String(50), nullable=True)
    prefix: Mapped[str | None] = mapped_column(String(50), nullable=True)
    default_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    min_value: Mapped[float | None] = mapped_column(Numeric(20, 10), nullable=True)
    max_value: Mapped[float | None] = mapped_column(Numeric(20, 10), nullable=True)
    step_value: Mapped[float | None] = mapped_column(Numeric(20, 10), nullable=True)
    options: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    validation_rules: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    conditional_rules: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("calculator_id", "key", name="uq_calculator_inputs_key"),
    )

    calculator = relationship("Calculator", back_populates="inputs")


class CalculatorOutput(UUIDMixin, TimestampMixin, SortOrderMixin, BaseModel):
    __tablename__ = "calculator_outputs"

    calculator_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("calculators.id", ondelete="CASCADE"), nullable=False
    )
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_type: Mapped[str] = mapped_column(String(50), nullable=False)
    data_type: Mapped[str] = mapped_column(String(50), nullable=False, default="number")
    prefix: Mapped[str | None] = mapped_column(String(50), nullable=True)
    suffix: Mapped[str | None] = mapped_column(String(50), nullable=True)
    format: Mapped[str | None] = mapped_column(String(50), nullable=True)
    decimal_places: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    chart_data_mapping: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        UniqueConstraint("calculator_id", "key", name="uq_calculator_outputs_key"),
    )

    calculator = relationship("Calculator", back_populates="outputs")


class CalculatorFormula(UUIDMixin, TimestampMixin, SortOrderMixin, BaseModel):
    __tablename__ = "calculator_formulas"

    calculator_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("calculators.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    formula_text: Mapped[str] = mapped_column(Text, nullable=False)
    formula_python: Mapped[str | None] = mapped_column(Text, nullable=True)
    formula_javascript: Mapped[str | None] = mapped_column(Text, nullable=True)
    variables: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    calculator = relationship("Calculator", back_populates="formulas")


class CalculatorFAQ(UUIDMixin, TimestampMixin, SortOrderMixin, BaseModel):
    __tablename__ = "calculator_faqs"

    calculator_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("calculators.id", ondelete="CASCADE"), nullable=False
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    schema_type: Mapped[str] = mapped_column(String(50), nullable=False, default="FAQPage")
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    calculator = relationship("Calculator", back_populates="faqs")


class CalculatorExample(UUIDMixin, TimestampMixin, SortOrderMixin, BaseModel):
    __tablename__ = "calculator_examples"

    calculator_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("calculators.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_values: Mapped[dict] = mapped_column(JSONB, nullable=False)
    expected_outputs: Mapped[dict] = mapped_column(JSONB, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    calculator = relationship("Calculator", back_populates="examples")


class CalculatorReference(UUIDMixin, TimestampMixin, SortOrderMixin, BaseModel):
    __tablename__ = "calculator_references"

    calculator_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("calculators.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    citation_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    calculator = relationship("Calculator", back_populates="references")


class CalculatorChart(UUIDMixin, TimestampMixin, SortOrderMixin, BaseModel):
    __tablename__ = "calculator_charts"

    calculator_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("calculators.id", ondelete="CASCADE"), nullable=False
    )
    chart_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_mapping: Mapped[dict] = mapped_column(JSONB, nullable=False)
    options: Mapped[dict | None] = mapped_column(JSONB, default=dict, nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    calculator = relationship("Calculator", back_populates="charts")


class CalculatorSection(UUIDMixin, TimestampMixin, SortOrderMixin, BaseModel):
    __tablename__ = "calculator_sections"

    calculator_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("calculators.id", ondelete="CASCADE"), nullable=False
    )
    section_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    calculator = relationship("Calculator", back_populates="sections")


class RelatedCalculator(UUIDMixin, TimestampMixin, BaseModel):
    __tablename__ = "related_calculators"

    calculator_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("calculators.id", ondelete="CASCADE"), nullable=False
    )
    related_calculator_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("calculators.id", ondelete="CASCADE"), nullable=False
    )
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False, default="related")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint("calculator_id", "related_calculator_id", name="uq_related_calculators"),
        CheckConstraint("calculator_id != related_calculator_id", name="ck_related_calculators_no_self"),
    )

    calculator = relationship("Calculator", back_populates="related_calculators", foreign_keys=[calculator_id])
    related = relationship("Calculator", foreign_keys=[related_calculator_id])


class Guide(UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, SortOrderMixin, SlugMixin, BaseModel):
    __tablename__ = "guides"

    category_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    author_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("authors.id", ondelete="SET NULL"), nullable=True
    )
    reviewer_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("reviewers.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    subtitle: Mapped[str | None] = mapped_column(String(500), nullable=True)
    excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    reading_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    difficulty_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    published_at: Mapped[datetime | None] = mapped_column(nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(nullable=True)
    seo_metadata_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("seo_metadata.id", ondelete="SET NULL"), nullable=True
    )

    __table_args__ = (
        CheckConstraint("status IN ('draft', 'published', 'archived', 'scheduled')", name="ck_guides_status"),
    )

    category = relationship("Category", back_populates="guides")
    author = relationship("Author", back_populates="guides")
    reviewer = relationship("Reviewer", back_populates="guides")
    seo_metadata = relationship("SEOMetadata", lazy="joined")
    sections = relationship("GuideSection", back_populates="guide", lazy="selectin", cascade="all, delete-orphan")
    calculators = relationship("GuideCalculator", back_populates="guide", lazy="selectin", cascade="all, delete-orphan")
    media = relationship("GuideMedia", back_populates="guide", lazy="selectin", cascade="all, delete-orphan")


class GuideSection(UUIDMixin, TimestampMixin, SortOrderMixin, BaseModel):
    __tablename__ = "guide_sections"

    guide_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("guides.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    section_type: Mapped[str] = mapped_column(String(50), default="text", nullable=True)
    anchor_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    calculator_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("calculators.id", ondelete="SET NULL"), nullable=True
    )
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    guide = relationship("Guide", back_populates="sections")


class GuideCalculator(UUIDMixin, TimestampMixin, SortOrderMixin, BaseModel):
    __tablename__ = "guide_calculators"

    guide_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("guides.id", ondelete="CASCADE"), nullable=False
    )
    calculator_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("calculators.id", ondelete="CASCADE"), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("guide_id", "calculator_id", name="uq_guide_calculators"),
    )

    guide = relationship("Guide", back_populates="calculators")
    calculator = relationship("Calculator")


class BlogPost(UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, SlugMixin, BaseModel):
    __tablename__ = "blog_posts"

    category_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    author_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("authors.id", ondelete="SET NULL"), nullable=True
    )
    reviewer_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("reviewers.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    subtitle: Mapped[str | None] = mapped_column(String(500), nullable=True)
    excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    reading_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    published_at: Mapped[datetime | None] = mapped_column(nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(nullable=True)
    seo_metadata_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("seo_metadata.id", ondelete="SET NULL"), nullable=True
    )

    __table_args__ = (
        CheckConstraint("status IN ('draft', 'published', 'archived', 'scheduled')", name="ck_blog_posts_status"),
    )

    category = relationship("Category", back_populates="blog_posts")
    author = relationship("Author", back_populates="blog_posts")
    reviewer = relationship("Reviewer", back_populates="blog_posts")
    seo_metadata = relationship("SEOMetadata", lazy="joined")
    sections = relationship("BlogSection", back_populates="blog_post", lazy="selectin", cascade="all, delete-orphan")
    calculators = relationship("BlogCalculator", back_populates="blog_post", lazy="selectin", cascade="all, delete-orphan")
    media = relationship("BlogMedia", back_populates="blog_post", lazy="selectin", cascade="all, delete-orphan")


class BlogSection(UUIDMixin, TimestampMixin, SortOrderMixin, BaseModel):
    __tablename__ = "blog_sections"

    blog_post_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("blog_posts.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    section_type: Mapped[str] = mapped_column(String(50), default="text", nullable=True)
    anchor_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    calculator_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("calculators.id", ondelete="SET NULL"), nullable=True
    )
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    blog_post = relationship("BlogPost", back_populates="sections")


class GlossaryTerm(UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, SortOrderMixin, BaseModel):
    __tablename__ = "glossary_terms"

    term: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(500), nullable=False, unique=True, index=True)
    definition: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    related_terms: Mapped[list | None] = mapped_column(ARRAY(String(255)), nullable=True)
    seo_metadata_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("seo_metadata.id", ondelete="SET NULL"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="published")


class FAQ(UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, SortOrderMixin, BaseModel):
    __tablename__ = "faqs"

    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="published")


class BlogCalculator(UUIDMixin, TimestampMixin, SortOrderMixin, BaseModel):
    __tablename__ = "blog_calculators"

    blog_post_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("blog_posts.id", ondelete="CASCADE"), nullable=False
    )
    calculator_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("calculators.id", ondelete="CASCADE"), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("blog_post_id", "calculator_id", name="uq_blog_calculators"),
    )

    blog_post = relationship("BlogPost", back_populates="calculators")
    calculator = relationship("Calculator")
