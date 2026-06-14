"""
Pydantic schemas para validação de dados de usuário.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.schemas.role import RoleOut


class UserCreate(BaseModel):
    """Schema para registro público de novo usuário (sem role_id)."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)

    class Config:
        from_attributes = True


class UserCreateWithRole(BaseModel):
    """Schema para criar usuário via endpoint /users com role_id (requer permissão)."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role_id: int = Field(..., gt=0)

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema para atualizar dados do usuário."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    active: Optional[bool] = None

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    """Schema para retornar dados do usuário na API."""
    id: int
    email: str
    first_name: str
    last_name: str
    active: bool
    role: RoleOut
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    """Schema para requisição de mudança de senha do usuário logado."""
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

    class Config:
        from_attributes = True
