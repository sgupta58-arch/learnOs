from pydantic import BaseModel, EmailStr, Field


class LoginRequestSchema(BaseModel):
    """Schema for user login request."""

    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class TokenResponseSchema(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str = "bearer"