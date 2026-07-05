from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_admin
from app.models.audit import AuditLog
from app.models.auth import User
from app.schemas.common import paginated_response, success_response

router = APIRouter(prefix="/audit-logs", tags=["Admin - Audit"])


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str | None = None
    action: str
    resource_type: str
    resource_id: str | None = None
    details: dict | None = None
    changes: dict | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    severity: str
    created_at: datetime


@router.get("", response_model=dict)
def list_audit_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user_id: str | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    severity: str | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    query = db.query(AuditLog)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    if severity:
        query = query.filter(AuditLog.severity == severity)
    total = query.count()
    items = query.order_by(AuditLog.created_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()
    return paginated_response(
        data=[AuditLogResponse.model_validate(log).model_dump() for log in items],
        total=total,
        page=page,
        per_page=per_page,
    )
