from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class CheckoutRequest(BaseModel):
    provider: str  # stripe, paypal, razorpay, jazzcash, easypaisa
    plan_id: int
    billing_cycle: str  # monthly, yearly

class CheckoutResponse(BaseModel):
    checkout_url: str

class SubscriptionPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    stripe_price_id_monthly: Optional[str] = None
    stripe_price_id_yearly: Optional[str] = None
    price_monthly: float
    price_yearly: float
    features: Optional[dict] = None

class SubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    plan: SubscriptionPlanResponse
    status: str
    billing_cycle: str
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool
