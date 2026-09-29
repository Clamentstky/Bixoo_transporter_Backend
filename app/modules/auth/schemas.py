from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

class EmailCredentials(BaseModel):
    email: EmailStr

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        return value.strip().lower() if isinstance(value, str) else value

class LoginRequest(EmailCredentials):
    password: str = Field(min_length=1, max_length=128)

class RegisterRequest(EmailCredentials):
    name: str = Field(min_length=1, max_length=255)
    mobile: str = Field(pattern=r"^\d{10}$")
    password: str = Field(min_length=8, max_length=128)
    vehicleType: str = Field(min_length=1, max_length=100)
    vehicleNumber: str = Field(min_length=1, max_length=50)
    capacity: str
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=1, max_length=100)

    @field_validator("name", "mobile", "vehicleType", "vehicleNumber", "city", "state", mode="before")
    @classmethod
    def trim_text(cls, value):
        return value.strip() if isinstance(value, str) else value

class RefreshRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    mobile: str
    role: str
    status: str
    
    class Config:
        from_attributes = True

class LoginResponse(TokenResponse):
    user: UserResponse
