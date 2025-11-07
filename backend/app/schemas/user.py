"""User schemas for authentication and user management"""

from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    username: str
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    """Schema for creating new user"""
    password: str


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: datetime | None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str


class Token(BaseModel):
    """Schema for JWT token"""
    access_token: str
    token_type: str
