"""
Pacote de models (tabelas) do banco de dados.

Cada módulo do sistema (usuários, produtos, clientes, vendas, estoque...)
terá seu próprio arquivo aqui (ex: user.py, product.py, sale.py).

IMPORTANTE: todo novo model criado deve ser importado neste arquivo.
Isso garante que:
  1. O Alembic consiga "ver" a tabela e gerar migrações automaticamente
     (via `from app.models import *` em alembic/env.py).
  2. Os relacionamentos entre tabelas (ForeignKey/relationship) sejam
     resolvidos corretamente pelo SQLAlchemy.
"""

# Módulo 1: Autenticação e Usuários
from app.models.user import Role, User, PasswordReset

# Módulo 2: Produtos e Categorias
from app.models.product import Category, Product, StockMovement

__all__ = [
    # Módulo 1
    "Role",
    "User",
    "PasswordReset",
    # Módulo 2
    "Category",
    "Product",
    "StockMovement",
]
