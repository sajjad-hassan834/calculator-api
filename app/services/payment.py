from abc import ABC, abstractmethod
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import PaymentTransaction, SubscriptionPlan, UserSubscription


class PaymentGateway(ABC):
    """Abstract base class for all payment gateways."""

    @abstractmethod
    async def create_checkout_session(
        self, user: Any, plan: SubscriptionPlan, billing_cycle: str
    ) -> str:
        """Create a checkout session/URL for the user."""
        pass

    @abstractmethod
    async def create_subscription(
        self, user: Any, plan: SubscriptionPlan, billing_cycle: str, payment_method_id: str
    ) -> Dict[str, Any]:
        """Directly create a subscription (if gateway supports it without checkout UI)."""
        pass

    @abstractmethod
    async def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel an active subscription."""
        pass

    @abstractmethod
    async def verify_webhook(self, payload: bytes, headers: dict) -> Dict[str, Any]:
        """Verify webhook signature and return parsed event data."""
        pass


class StripeGateway(PaymentGateway):
    def __init__(self, api_key: str, webhook_secret: str):
        self.api_key = api_key
        self.webhook_secret = webhook_secret

    async def create_checkout_session(self, user: Any, plan: SubscriptionPlan, billing_cycle: str) -> str:
        # TODO: Implement actual Stripe SDK call
        return f"https://checkout.stripe.com/pay/{plan.id}?user={user.id}"

    async def create_subscription(self, user: Any, plan: SubscriptionPlan, billing_cycle: str, payment_method_id: str) -> Dict[str, Any]:
        return {"status": "active", "provider_subscription_id": "sub_stripe123"}

    async def cancel_subscription(self, subscription_id: str) -> bool:
        return True

    async def verify_webhook(self, payload: bytes, headers: dict) -> Dict[str, Any]:
        return {"type": "invoice.payment_succeeded", "data": {}}


class PayPalGateway(PaymentGateway):
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    async def create_checkout_session(self, user: Any, plan: SubscriptionPlan, billing_cycle: str) -> str:
        return f"https://paypal.com/checkoutnow?token=EC-1234567890"

    async def create_subscription(self, user: Any, plan: SubscriptionPlan, billing_cycle: str, payment_method_id: str) -> Dict[str, Any]:
        return {"status": "active", "provider_subscription_id": "I-PAYPAL123"}

    async def cancel_subscription(self, subscription_id: str) -> bool:
        return True

    async def verify_webhook(self, payload: bytes, headers: dict) -> Dict[str, Any]:
        return {"type": "PAYMENT.SALE.COMPLETED", "data": {}}


class RazorpayGateway(PaymentGateway):
    def __init__(self, key_id: str, key_secret: str):
        self.key_id = key_id
        self.key_secret = key_secret

    async def create_checkout_session(self, user: Any, plan: SubscriptionPlan, billing_cycle: str) -> str:
        return f"https://checkout.razorpay.com/v1/checkout.js?order_id=order_123"

    async def create_subscription(self, user: Any, plan: SubscriptionPlan, billing_cycle: str, payment_method_id: str) -> Dict[str, Any]:
        return {"status": "active", "provider_subscription_id": "sub_razor123"}

    async def cancel_subscription(self, subscription_id: str) -> bool:
        return True

    async def verify_webhook(self, payload: bytes, headers: dict) -> Dict[str, Any]:
        return {"event": "subscription.charged", "payload": {}}


class JazzCashGateway(PaymentGateway):
    def __init__(self, merchant_id: str, password: str):
        self.merchant_id = merchant_id
        self.password = password

    async def create_checkout_session(self, user: Any, plan: SubscriptionPlan, billing_cycle: str) -> str:
        return f"https://sandbox.jazzcash.com.pk/CustomerPortal/transactionmanagement/merchantform"

    async def create_subscription(self, user: Any, plan: SubscriptionPlan, billing_cycle: str, payment_method_id: str) -> Dict[str, Any]:
        raise NotImplementedError("JazzCash requires manual renewal (no auto-recurring subscriptions via basic API)")

    async def cancel_subscription(self, subscription_id: str) -> bool:
        return True

    async def verify_webhook(self, payload: bytes, headers: dict) -> Dict[str, Any]:
        return {"pp_ResponseCode": "000", "data": {}}


class EasyPaisaGateway(PaymentGateway):
    def __init__(self, store_id: str, hash_key: str):
        self.store_id = store_id
        self.hash_key = hash_key

    async def create_checkout_session(self, user: Any, plan: SubscriptionPlan, billing_cycle: str) -> str:
        return f"https://easypay.easypaisa.com.pk/easypay/Index.jsf"

    async def create_subscription(self, user: Any, plan: SubscriptionPlan, billing_cycle: str, payment_method_id: str) -> Dict[str, Any]:
        raise NotImplementedError("EasyPaisa requires manual renewal")

    async def cancel_subscription(self, subscription_id: str) -> bool:
        return True

    async def verify_webhook(self, payload: bytes, headers: dict) -> Dict[str, Any]:
        return {"status": "SUCCESS", "data": {}}


class PaymentService:
    """Service to orchestrate payments across multiple gateways."""

    def __init__(self):
        from app.core.settings import settings

        self.gateways = {
            "stripe": StripeGateway(settings.stripe_secret_key, settings.stripe_webhook_secret),
            "paypal": PayPalGateway(settings.paypal_client_id, settings.paypal_client_secret),
            "razorpay": RazorpayGateway(settings.razorpay_key_id, settings.razorpay_key_secret),
            "jazzcash": JazzCashGateway(settings.jazzcash_merchant_id, settings.jazzcash_password),
            "easypaisa": EasyPaisaGateway(settings.easypaisa_store_id, settings.easypaisa_token),
        }

    def get_gateway(self, provider: str) -> PaymentGateway:
        gateway = self.gateways.get(provider.lower())
        if not gateway:
            raise ValueError(f"Payment provider '{provider}' is not supported.")
        return gateway

    async def create_checkout(self, provider: str, user: Any, plan: SubscriptionPlan, billing_cycle: str) -> str:
        gateway = self.get_gateway(provider)
        return await gateway.create_checkout_session(user, plan, billing_cycle)

    async def handle_webhook(
        self, db: AsyncSession, provider: str, payload: bytes, headers: dict
    ) -> None:
        gateway = self.get_gateway(provider)
        event = await gateway.verify_webhook(payload, headers)
        
        # In a real implementation, we would map the gateway-specific event 
        # to our internal database updates here.
        # e.g., if event indicates payment success -> mark PaymentTransaction as 'completed'
        pass
