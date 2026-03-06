from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from app.models import UserRole, JobStatus


# Auth Schemas
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str  # username
    exp: datetime
    iat: datetime
    role: UserRole


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    role: UserRole
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    pass


class JobCreate(BaseModel):
    input_data: dict
    job_type: str = "default"  # Type of job to process


class JobUpdate(BaseModel):
    status: JobStatus
    progress: Optional[int] = None
    result: Optional[dict] = None
    error: Optional[str] = None


class JobResponse(BaseModel):
    id: int
    user_id: int
    status: JobStatus
    progress: int
    job_type: str
    input_data: Optional[dict] = None
    result: Optional[dict] = None
    error: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    items: list[JobResponse]
    total: int
    skip: int
    limit: int


# Health Check
class HealthResponse(BaseModel):
    status: str
    app_name: str
    debug: bool
