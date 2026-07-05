from datetime import datetime
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginResponse(BaseModel):
    success: bool = True
    message: str = "Login successful"
    data: TokenResponse | None = None


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str | None = None
    display_name: str | None = None


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    display_name: str | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: str
    email: str
    username: str | None = None
    is_active: bool
    is_superadmin: bool
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
