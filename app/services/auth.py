from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.core.settings import settings
from app.exceptions import UnauthorizedException
from app.models.auth import Role, User, UserRole, UserSession


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate(self, email: str, password: str) -> dict:
        user = self.db.query(User).filter(
            User.email == email,
            User.deleted_at.is_(None),
        ).first()
        if not user or not verify_password(password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")
        user.last_login_at = datetime.now(UTC)
        access_token = create_access_token({"sub": user.id})
        refresh_token = create_refresh_token({"sub": user.id})
        self.db.commit()
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    def refresh_token(self, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid refresh token")
        user_id = payload.get("sub")
        user = self.db.query(User).filter(
            User.id == user_id,
            User.deleted_at.is_(None),
            User.is_active == True,
        ).first()
        if not user:
            raise UnauthorizedException("User not found")
        return {
            "access_token": create_access_token({"sub": user.id}),
            "refresh_token": create_refresh_token({"sub": user.id}),
            "token_type": "bearer",
        }

    def create_user(self, email: str, password: str, username: str | None = None) -> User:
        user = User(
            email=email,
            username=username,
            password_hash=get_password_hash(password),
        )
        is_first = self.db.query(User).count() == 0
        make_admin = is_first or settings.is_development
        if make_admin:
            user.is_superadmin = True
        self.db.add(user)
        self.db.flush()
        if make_admin:
            role = self.db.query(Role).filter(Role.slug == "super-admin").first()
            if role:
                user_role = UserRole(user_id=user.id, role_id=role.id)
                self.db.add(user_role)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_id(self, user_id: str) -> User | None:
        return self.db.query(User).filter(
            User.id == user_id,
            User.deleted_at.is_(None),
        ).first()

    def get_user_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(
            User.email == email,
            User.deleted_at.is_(None),
        ).first()
