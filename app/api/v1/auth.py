from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.exceptions import BadRequestException
from app.models.auth import User
from app.schemas.auth import LoginRequest, UserCreate, UserResponse
from app.schemas.common import success_response
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    result = auth_service.authenticate(request.email, request.password)
    return success_response(data=result, message="Login successful")


@router.post("/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    existing = auth_service.get_user_by_email(user_data.email)
    if existing:
        raise BadRequestException("Email already registered")
    user = auth_service.create_user(
        email=user_data.email,
        password=user_data.password,
        username=user_data.username,
    )
    return success_response(
        data=UserResponse.model_validate(user).model_dump(),
        message="User created successfully",
    )


@router.post("/refresh")
def refresh_token(token_data: dict, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    result = auth_service.refresh_token(token_data.get("refresh_token", ""))
    return success_response(data=result, message="Token refreshed")


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return success_response(
        data=UserResponse.model_validate(current_user).model_dump(),
        message="Current user retrieved",
    )
