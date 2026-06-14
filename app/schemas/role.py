"""
Pydantic schemas para validação de dados de entrada e saída da API de autenticação.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RoleBase(BaseModel):
    """Base para Role - usado em criar e atualizar."""
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    permissions: list[str] = Field(default_factory=list)  # Ex: ["users:read", "users:write"]


class RoleCreate(RoleBase):
    """Schema para criar uma nova Role."""
    pass


class RoleOut(RoleBase):
    """Schema para retornar uma Role na API."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
