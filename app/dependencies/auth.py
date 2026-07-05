from collections.abc import Awaitable, Callable

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token, security_scheme
from app.database.session import get_db
from app.exceptions import ForbiddenException, UnauthorizedException
from app.models.auth import Permission, Role, RolePermission, User, UserRole

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_token(credentials.credentials)
    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException("Invalid token payload")
    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if user is None:
        raise UnauthorizedException("User not found")
    if not user.is_active:
        raise UnauthorizedException("User is deactivated")
    return user


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    user = get_current_user(credentials, db)
    user_role_slugs = [ur.role.slug for ur in user.roles]
    if "super-admin" not in user_role_slugs and "admin" not in user_role_slugs:
        raise ForbiddenException("Admin access required")
    return user


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db),
) -> User | None:
    if credentials is None:
        return None
    try:
        return get_current_user(credentials, db)
    except Exception:
        return None


class RoleDependency:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        user_role_slugs = {ur.role.slug for ur in current_user.roles}
        if not any(role in user_role_slugs for role in self.allowed_roles):
            raise ForbiddenException(
                f"Requires one of roles: {', '.join(self.allowed_roles)}"
            )
        return current_user


class PermissionDependency:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.is_superadmin:
            return current_user
        user_permissions = set()
        for user_role in current_user.roles:
            for rp in user_role.role.permissions:
                perm = rp.permission
                user_permissions.add(f"{perm.resource}:{perm.action}")
        if self.required_permission not in user_permissions:
            raise ForbiddenException(
                f"Required permission: {self.required_permission}"
            )
        return current_user


def require_role(role_slug: str) -> Callable[[User], User]:
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role_slugs = {ur.role.slug for ur in current_user.roles}
        if role_slug not in user_role_slugs and "super-admin" not in user_role_slugs:
            raise ForbiddenException(f"Requires role: {role_slug}")
        return current_user
    return role_checker


def require_permission(resource: str, action: str) -> Callable[[User], User]:
    required = f"{resource}:{action}"
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.is_superadmin:
            return current_user
        user_permissions = set()
        for user_role in current_user.roles:
            for rp in user_role.role.permissions:
                perm = rp.permission
                user_permissions.add(f"{perm.resource}:{perm.action}")
        if required not in user_permissions:
            raise ForbiddenException(f"Required permission: {required}")
        return current_user
    return permission_checker
