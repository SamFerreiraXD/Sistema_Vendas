"""
Modelos ORM para autenticação e gerenciamento de usuários.

Tabelas:
- Role: Define os papéis disponíveis no sistema (admin, gerente, vendedor, etc.)
- User: Dados do usuário com referência a um Role
- PasswordReset: Requisições de reset de senha com token único
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, Boolean, Integer
from sqlalchemy.orm import relationship

from app.core.database import Base


class Role(Base):
    """
    Define um papel (role) no sistema.
    Cada usuário tem um role que define suas permissões.
    """

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    permissions = Column(Text, nullable=False)  # JSON como string, ex: '["users:read", "users:write"]'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamento com User
    users = relationship("User", back_populates="role", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name})>"


class User(Base):
    """
    Usuário do sistema.
    Campos:
    - email: identificador único do usuário
    - hashed_password: senha hash com bcrypt
    - first_name, last_name: nome do usuário
    - role_id: referência à Role
    - active: ativa/desativa o usuário sem deletar registro
    - created_at, updated_at: timestamps
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamento com Role
    role = relationship("Role", back_populates="users")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, active={self.active})>"


class PasswordReset(Base):
    """
    Requisição de reset de senha.
    Cada requisição gera um token único com validade limitada.
    """

    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String(500), unique=True, nullable=False, index=True)
    expired = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    def __repr__(self):
        return f"<PasswordReset(id={self.id}, user_id={self.user_id}, expired={self.expired})>"
