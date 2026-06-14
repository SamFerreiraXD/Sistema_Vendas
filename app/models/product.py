"""
Modelos ORM para gerenciamento de produtos, categorias e estoque.

Tabelas:
- Category: Categorias de produtos
- Product: Produtos com preço e estoque
- StockMovement: Histórico de movimentação de estoque
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, Boolean, Integer, Float, Enum
from sqlalchemy.orm import relationship

from app.core.database import Base


class Category(Base):
    """
    Categoria de produtos.
    
    Campos:
    - name: Nome da categoria (ex: "Eletrônicos")
    - slug: URL-friendly identifier (ex: "eletronicos")
    - description: Descrição opcional
    - created_at, updated_at: timestamps
    """

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamento com Product
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name}, slug={self.slug})>"


class Product(Base):
    """
    Produto do sistema.
    
    Campos:
    - name: Nome do produto
    - description: Descrição detalhada
    - category_id: Referência à Category
    - sku: Stock Keeping Unit (único, para código interno)
    - barcode: Código de barras (EAN/UPC)
    - price_cost: Preço de custo
    - price_sale: Preço de venda
    - stock_quantity: Quantidade em estoque
    - active: Ativa/desativa o produto sem deletar (soft delete)
    - created_at, updated_at: timestamps
    """

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    barcode = Column(String(100), nullable=True, unique=True, index=True)
    price_cost = Column(Float, nullable=False)
    price_sale = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0, nullable=False, index=True)
    active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    category = relationship("Category", back_populates="products")
    stock_movements = relationship("StockMovement", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, sku={self.sku}, stock={self.stock_quantity})>"


class StockMovement(Base):
    """
    Registro de movimentação de estoque.
    
    Rastreia todas as entradas e saídas de estoque para auditoria.
    
    Campos:
    - product_id: Referência ao Product
    - type: "in" (entrada) ou "out" (saída)
    - quantity: Quantidade movimentada
    - reason: Motivo da movimentação (ex: "Venda", "Devolução", "Ajuste", "Compra")
    - user_id: Usuário que fez a movimentação
    - created_at: Data/hora da movimentação
    """

    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    type = Column(String(10), nullable=False)  # "in" ou "out"
    quantity = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=False)  # "Venda", "Devolução", "Compra", etc.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relacionamentos
    product = relationship("Product", back_populates="stock_movements")

    def __repr__(self):
        return f"<StockMovement(id={self.id}, product_id={self.product_id}, type={self.type}, qty={self.quantity})>"
