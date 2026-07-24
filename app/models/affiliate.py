from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, TimestampMixin, UUIDMixin


class AffiliatePartner(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "affiliate_partners"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    commission_rate: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(50), default="active")  # active, inactive, pending

    links: Mapped[list["AffiliateLink"]] = relationship(
        "AffiliateLink", back_populates="partner", cascade="all, delete-orphan"
    )


class AffiliateLink(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "affiliate_links"

    partner_id: Mapped[str] = mapped_column(
        ForeignKey("affiliate_partners.id", ondelete="CASCADE"), nullable=False
    )
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    utm_source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    utm_medium: Mapped[str | None] = mapped_column(String(100), nullable=True)
    utm_campaign: Mapped[str | None] = mapped_column(String(100), nullable=True)
    clicks: Mapped[int] = mapped_column(Integer, default=0)

    partner: Mapped["AffiliatePartner"] = relationship(
        "AffiliatePartner", back_populates="links"
    )
    conversions: Mapped[list["AffiliateConversion"]] = relationship(
        "AffiliateConversion", back_populates="link", cascade="all, delete-orphan"
    )


class AffiliateConversion(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "affiliate_conversions"

    link_id: Mapped[str] = mapped_column(
        ForeignKey("affiliate_links.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    commission_earned: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, paid, rejected
    transaction_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)

    link: Mapped["AffiliateLink"] = relationship(
        "AffiliateLink", back_populates="conversions"
    )
