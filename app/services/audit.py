from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.audit import AuditLog


class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        user_id: str | None = None,
        details: dict | None = None,
        changes: dict | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        severity: str = "info",
    ) -> AuditLog:
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            severity=severity,
            created_at=datetime.now(UTC),
        )
        self.db.add(log_entry)
        self.db.commit()
        return log_entry

    def get_logs(
        self,
        resource_type: str | None = None,
        resource_id: str | None = None,
        action: str | None = None,
        user_id: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[AuditLog]:
        query = self.db.query(AuditLog)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if resource_id:
            query = query.filter(AuditLog.resource_id == resource_id)
        if action:
            query = query.filter(AuditLog.action == action)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        return query.order_by(AuditLog.id.desc()).offset(skip).limit(limit).all()
