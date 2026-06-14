"""
Pydantic schemas para validação de dados de produtos, categorias e estoque.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# -----------------------------------------------------------------------
# CATEGORY SCHEMAS
# -----------------------------------------------------------------------

class CategoryBase(BaseModel):
    """Base para Category - usado em criar e atualizar."""
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None)

    class Config:
        from_attributes = True


class CategoryCreate(CategoryBase):
    """Schema para criar uma nova Category."""
    pass


class CategoryOut(CategoryBase):
    """Schema para retornar uma Category na API."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# -----------------------------------------------------------------------
# PRODUCT SCHEMAS
# -----------------------------------------------------------------------

class ProductBase(BaseModel):
    """Base para Product - usado em criar e atualizar."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None)
    category_id: int = Field(..., gt=0)
    sku: str = Field(..., min_length=1, max_length=100)
    barcode: Optional[str] = Field(None, max_length=100)
    price_cost: float = Field(..., gt=0)
    price_sale: float = Field(..., gt=0)

    class Config:
        from_attributes = True


class ProductCreate(ProductBase):
    """Schema para criar um novo Product."""
    pass


class ProductUpdate(BaseModel):
    """Schema para atualizar dados do Product."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None)
    category_id: Optional[int] = Field(None, gt=0)
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    barcode: Optional[str] = Field(None, max_length=100)
    price_cost: Optional[float] = Field(None, gt=0)
    price_sale: Optional[float] = Field(None, gt=0)
    active: Optional[bool] = None

    class Config:
        from_attributes = True


class ProductOut(ProductBase):
    """Schema para retornar um Product na API."""
    id: int
    stock_quantity: int
    active: bool
    created_at: datetime
    updated_at: datetime
    category: CategoryOut

    class Config:
        from_attributes = True


# -----------------------------------------------------------------------
# STOCK MOVEMENT SCHEMAS
# -----------------------------------------------------------------------

class StockMovementBase(BaseModel):
    """Base para StockMovement."""
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    reason: str = Field(..., min_length=1, max_length=255)

    class Config:
        from_attributes = True


class StockMovementCreate(StockMovementBase):
    """Schema para registrar uma movimentação de estoque."""
    type: str = Field(..., pattern="^(in|out)$")  # "in" ou "out"


class StockMovementOut(StockMovementBase):
    """Schema para retornar uma movimentação de estoque."""
    id: int
    type: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
