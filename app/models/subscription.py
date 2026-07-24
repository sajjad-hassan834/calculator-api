"""
Subscription, Payment & API Key models.
Supports multi-gateway: Stripe, PayPal, Razorpay, JazzCash, EasyPaisa.
"""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
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
    TimestampMixin,
    UUIDMixin,
)


# ============================================================
# Subscription Plans
# ============================================================

class SubscriptionPlan(UUIDMixin, TimestampMixin, SoftDeleteMixin, SortOrderMixin, BaseModel):
    """Defines pricing tiers: Free / Pro / Enterprise / Custom."""
    __tablename__ = "subscription_plans"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tagline: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Pricing — stored in cents/smallest unit to avoid float issues
    price_monthly: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # in cents
    price_yearly: Mapped[int] = mapped_column(Integer, nullable=False, default=0)   # in cents
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")

    # Features & Limits (flexible JSONB)
    features: Mapped[dict | None] = mapped_column(JSONB, default=dict, nullable=True)
    limits: Mapped[dict | None] = mapped_column(JSONB, default=dict, nullable=True)
    # Example limits: {"calculations_per_day": 100, "pdf_exports_per_month": 10, "api_calls_per_day": 1000}

    trial_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_free: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Multi-gateway price IDs
    stripe_price_id_monthly: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_price_id_yearly: Mapped[str | None] = mapped_column(String(255), nullable=True)
    paypal_plan_id_monthly: Mapped[str | None] = mapped_column(String(255), nullable=True)
    paypal_plan_id_yearly: Mapped[str | None] = mapped_column(String(255), nullable=True)
    razorpay_plan_id_monthly: Mapped[str | None] = mapped_column(String(255), nullable=True)
    razorpay_plan_id_yearly: Mapped[str | None] = mapped_column(String(255), nullable=True)

    subscriptions = relationship("UserSubscription", back_populates="plan", lazy="selectin")


# ============================================================
# User Subscriptions
# ============================================================

class UserSubscription(UUIDMixin, TimestampMixin, BaseModel):
    """Tracks a user's active subscription."""
    __tablename__ = "user_subscriptions"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    plan_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("subscription_plans.id", ondelete="RESTRICT"), nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active"
    )
    # statuses: active, cancelled, expired, past_due, trialing, paused

    billing_cycle: Mapped[str] = mapped_column(
        String(20), nullable=False, default="monthly"
    )
    # billing_cycle: monthly, yearly, lifetime

    # Payment gateway info
    payment_gateway: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # gateways: stripe, paypal, razorpay, jazzcash, easypaisa, bank_transfer, manual
    gateway_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    gateway_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Period tracking
    current_period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    trial_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    trial_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'cancelled', 'expired', 'past_due', 'trialing', 'paused')",
            name="ck_user_subscriptions_status",
        ),
        CheckConstraint(
            "billing_cycle IN ('monthly', 'yearly', 'lifetime')",
            name="ck_user_subscriptions_billing_cycle",
        ),
        Index("idx_user_subscriptions_user_status", "user_id", "status"),
    )

    user = relationship("User", backref="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    transactions = relationship("PaymentTransaction", back_populates="subscription", lazy="selectin")


# ============================================================
# Payment Transactions
# ============================================================

class PaymentTransaction(UUIDMixin, TimestampMixin, BaseModel):
    """Records every payment event across all gateways."""
    __tablename__ = "payment_transactions"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    subscription_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("user_subscriptions.id", ondelete="SET NULL"), nullable=True
    )

    # Amount in smallest currency unit (cents, paisa, etc.)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    # statuses: pending, completed, failed, refunded, disputed

    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False, default="subscription")
    # types: subscription, one_time, refund, upgrade, downgrade

    # Gateway info
    payment_gateway: Mapped[str] = mapped_column(String(50), nullable=False)
    gateway_transaction_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    gateway_response: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Invoice
    invoice_number: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True)
    invoice_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metadata
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # For local gateways (JazzCash, EasyPaisa)
    mobile_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    payment_method: Mapped[str | None] = mapped_column(String(50), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'completed', 'failed', 'refunded', 'disputed')",
            name="ck_payment_transactions_status",
        ),
        Index("idx_payment_transactions_user", "user_id"),
        Index("idx_payment_transactions_gateway", "payment_gateway", "gateway_transaction_id"),
    )

    user = relationship("User")
    subscription = relationship("UserSubscription", back_populates="transactions")


# ============================================================
# Plan Features (granular feature flags)
# ============================================================

class PlanFeature(UUIDMixin, TimestampMixin, BaseModel):
    """Individual feature definitions linked to plans."""
    __tablename__ = "plan_features"

    plan_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("subscription_plans.id", ondelete="CASCADE"), nullable=False
    )
    feature_key: Mapped[str] = mapped_column(String(100), nullable=False)
    feature_name: Mapped[str] = mapped_column(String(255), nullable=False)
    feature_value: Mapped[str | None] = mapped_column(Text, nullable=True)  # "true", "100", "unlimited"
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint("plan_id", "feature_key", name="uq_plan_features_key"),
    )

    plan = relationship("SubscriptionPlan")


# ============================================================
# Usage Tracking
# ============================================================

class UsageRecord(UUIDMixin, TimestampMixin, BaseModel):
    """Tracks usage per user for rate-limited features."""
    __tablename__ = "usage_records"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    feature_key: Mapped[str] = mapped_column(String(100), nullable=False)
    # feature_key: "calculations", "pdf_exports", "api_calls", "embeds"

    usage_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "feature_key", "period_start", name="uq_usage_records_period"),
        Index("idx_usage_records_user_feature", "user_id", "feature_key"),
    )


# ============================================================
# API Keys (for developer/business API access)
# ============================================================

class APIKey(UUIDMixin, TimestampMixin, SoftDeleteMixin, BaseModel):
    """API keys for programmatic calculator access."""
    __tablename__ = "api_keys"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(10), nullable=False)  # first 8 chars for display
    key_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    permissions: Mapped[dict | None] = mapped_column(JSONB, default=dict, nullable=True)

    rate_limit_per_minute: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    rate_limit_per_day: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    total_requests: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    allowed_domains: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    allowed_ips: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        Index("idx_api_keys_user", "user_id"),
        Index("idx_api_keys_prefix", "key_prefix"),
    )

    user = relationship("User")
