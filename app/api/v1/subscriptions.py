from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from loguru import logger

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.exceptions import BadRequestException, NotFoundException
from app.models.auth import User
from app.models.subscription import SubscriptionPlan, UserSubscription
from app.schemas.subscription import CheckoutRequest, CheckoutResponse, SubscriptionResponse
from app.schemas.common import success_response
from app.services.payment import PaymentService

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])
payment_service = PaymentService()

@router.post("/checkout", response_model=dict)
async def create_checkout_session(
    request: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == request.plan_id).first()
    if not plan:
        raise NotFoundException("Subscription plan not found")
        
    try:
        checkout_url = await payment_service.create_checkout(
            provider=request.provider,
            user=current_user,
            plan=plan,
            billing_cycle=request.billing_cycle
        )
        return success_response(data={"checkout_url": checkout_url}, message="Checkout session created")
    except ValueError as e:
        raise BadRequestException(str(e))
    except Exception as e:
        logger.error(f"Payment error: {e}")
        raise BadRequestException("Failed to initialize payment gateway")

@router.get("/my-plan")
def get_my_plan(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    subscription = db.query(UserSubscription).filter(
        UserSubscription.user_id == current_user.id,
        UserSubscription.status == "active"
    ).first()
    
    if not subscription:
        return success_response(data=None, message="No active subscription")
        
    return success_response(
        data=SubscriptionResponse.model_validate(subscription).model_dump(),
        message="Active subscription retrieved"
    )

@router.post("/webhook/{provider}")
async def payment_webhook(
    provider: str,
    request: Request,
    db: Session = Depends(get_db)
):
    payload = await request.body()
    headers = dict(request.headers)
    
    try:
        # In a real app this would be async session, but we use sync DB mostly
        # The handle_webhook uses AsyncSession in the service, but since we are stubbing
        # we can just pass the db
        await payment_service.handle_webhook(db, provider, payload, headers)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Webhook error for {provider}: {e}")
        raise BadRequestException("Webhook processing failed")
