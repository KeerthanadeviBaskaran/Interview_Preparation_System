from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    """
    Base Pydantic Schema containing shared attributes across User operations.
    """
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    """
    Pydantic Schema required for User Registration requests.
    Enforces email format validation and password requirement.
    """
    password: str


class UserUpdate(BaseModel):
    """
    Pydantic Schema used for updating User Profile details.
    All fields are optional to allow partial updates.
    """
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserLogin(BaseModel):
    """
    Pydantic Schema for JSON login requests.
    """
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """
    Pydantic Response Schema returned to clients.
    Excludes sensitive fields like hashed_password while enabling ORM compatibility.
    """
    id: int
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    # Pydantic v2 configuration to parse SQLAlchemy ORM objects seamlessly
    model_config = ConfigDict(from_attributes=True)
