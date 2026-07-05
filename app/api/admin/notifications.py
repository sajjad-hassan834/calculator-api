from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_admin
from app.models.auth import User
from app.models.future import Notification
from app.schemas.common import paginated_response, success_response

router = APIRouter(prefix="/notifications", tags=["Admin - Notifications"])


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    type: str
    title: str
    message: str | None = None
    data: dict | None = None
    is_read: bool
    read_at: str | None = None
    created_at: datetime
    updated_at: datetime


@router.get("", response_model=dict)
def list_notifications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user_id: str | None = None,
    type: str | None = None,
    is_read: bool | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    query = db.query(Notification)
    if user_id:
        query = query.filter(Notification.user_id == user_id)
    if type:
        query = query.filter(Notification.type == type)
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    total = query.count()
    items = query.order_by(Notification.created_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()
    return paginated_response(
        data=[NotificationResponse.model_validate(n).model_dump() for n in items],
        total=total,
        page=page,
        per_page=per_page,
    )
