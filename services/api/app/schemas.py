from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SubmissionBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    age: int = Field(ge=0, le=120)
    place_of_living: str = Field(min_length=1, max_length=120)
    gender: str = Field(min_length=1, max_length=40)
    country_of_origin: str = Field(min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)


class SubmissionResponse(SubmissionBase):
    id: str
    classification_result: str
    photo_path: str
    created_at: datetime

    class Config:
        orm_mode = True


class AdminFilter(BaseModel):
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    gender: Optional[str] = None
    place_of_living: Optional[str] = None
    country_of_origin: Optional[str] = None
