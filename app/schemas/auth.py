"""
Pydantic schemas para autenticação e tokens.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """Schema para retornar tokens JWT após login ou refresh."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # em segundos


class RefreshTokenRequest(BaseModel):
    """Schema para requisição de novo access_token usando refresh_token."""
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    """Schema para requisição de reset de senha."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Schema para confirmar reset de senha com token."""
    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)


class TokenPayload(BaseModel):
    """Payload interno do JWT (não exposto na API)."""
    sub: int  # user_id
    exp: datetime
    type: str  # "access" ou "refresh"
