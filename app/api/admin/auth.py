from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_admin, require_role
from app.exceptions import BadRequestException, NotFoundException
from app.models.auth import Role, User, UserRole
from app.schemas.auth import UserResponse, UserUpdate
from app.schemas.common import success_response

router = APIRouter(prefix="", tags=["Admin - Users"])


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    description: str | None = None
    is_system: bool
    sort_order: int


class UserRoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    role_id: str
    granted_by: str | None = None
    role: RoleResponse | None = None


@router.get("/users")
def list_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    users = db.query(User).filter(User.deleted_at.is_(None)).offset(skip).limit(limit).all()
    return success_response(
        data=[UserResponse.model_validate(u).model_dump() for u in users],
        message="Users retrieved",
    )


@router.get("/users/{id}")
def get_user(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == id, User.deleted_at.is_(None)).first()
    if not user:
        raise NotFoundException("User not found")
    return success_response(data=UserResponse.model_validate(user).model_dump())


@router.put("/users/{id}")
def update_user(
    id: str,
    request: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    user = db.query(User).filter(User.id == id, User.deleted_at.is_(None)).first()
    if not user:
        raise NotFoundException("User not found")
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return success_response(
        data=UserResponse.model_validate(user).model_dump(),
        message="User updated successfully",
    )


@router.delete("/users/{id}")
def delete_user(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    user = db.query(User).filter(User.id == id, User.deleted_at.is_(None)).first()
    if not user:
        raise NotFoundException("User not found")
    user.deleted_at = datetime.now(UTC)
    db.commit()
    return success_response(message="User deleted successfully")


@router.get("/roles")
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    roles = db.query(Role).filter(Role.deleted_at.is_(None)).order_by(Role.sort_order.asc()).all()
    return success_response(
        data=[RoleResponse.model_validate(r).model_dump() for r in roles],
        message="Roles retrieved",
    )


@router.get("/users/{id}/roles")
def get_user_roles(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == id, User.deleted_at.is_(None)).first()
    if not user:
        raise NotFoundException("User not found")
    user_roles = db.query(UserRole).filter(UserRole.user_id == id).all()
    return success_response(
        data=[UserRoleResponse.model_validate(ur).model_dump() for ur in user_roles],
        message="User roles retrieved",
    )


@router.post("/users/{user_id}/roles/{role_slug}")
def assign_role(
    user_id: str,
    role_slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if not user:
        raise NotFoundException("User not found")
    role = db.query(Role).filter(Role.slug == role_slug, Role.deleted_at.is_(None)).first()
    if not role:
        raise NotFoundException("Role not found")
    existing = db.query(UserRole).filter(
        UserRole.user_id == user_id, UserRole.role_id == role.id
    ).first()
    if existing:
        raise BadRequestException("User already has this role")
    user_role = UserRole(user_id=user_id, role_id=role.id, granted_by=current_user.id)
    db.add(user_role)
    db.commit()
    return success_response(message=f"Role '{role_slug}' assigned to user")


@router.delete("/users/{user_id}/roles/{role_slug}")
def remove_role(
    user_id: str,
    role_slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if not user:
        raise NotFoundException("User not found")
    role = db.query(Role).filter(Role.slug == role_slug, Role.deleted_at.is_(None)).first()
    if not role:
        raise NotFoundException("Role not found")
    user_role = db.query(UserRole).filter(
        UserRole.user_id == user_id, UserRole.role_id == role.id
    ).first()
    if not user_role:
        raise NotFoundException("User does not have this role")
    db.delete(user_role)
    db.commit()
    return success_response(message=f"Role '{role_slug}' removed from user")
