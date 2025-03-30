"""
Pydantic schemas for authentication API.
"""
from datetime import datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    """Base schema for User."""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    """Schema for creating a User."""
    password: str


class RoleBase(BaseModel):
    """Base schema for Role."""
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    """Schema for creating a Role."""
    pass


class PrivilegeBase(BaseModel):
    """Base schema for Privilege."""
    name: str
    description: Optional[str] = None


class PrivilegeCreate(PrivilegeBase):
    """Schema for creating a Privilege."""
    pass


class PrivilegeResponse(PrivilegeBase):
    """Schema for Privilege response."""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class RoleResponse(RoleBase):
    """Schema for Role response."""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    privileges: List[PrivilegeResponse] = []

    class Config:
        orm_mode = True


class UserResponse(UserBase):
    """Schema for User response."""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    roles: List[RoleResponse] = []

    class Config:
        orm_mode = True


class Token(BaseModel):
    """Schema for authentication token."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str


class TokenPayload(BaseModel):
    """Schema for token payload."""
    sub: Optional[str] = None
    exp: Optional[int] = None


class RefreshToken(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str


class UserRoleCreate(BaseModel):
    """Schema for assigning a role to a user."""
    role_id: uuid.UUID


class RolePrivilegeCreate(BaseModel):
    """Schema for assigning a privilege to a role."""
    privilege_id: uuid.UUID


class LoginRequest(BaseModel):
    """Schema for login request."""
    username: str
    password: str
