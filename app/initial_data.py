"""
Script de seed para dados iniciais.

Cria:
- Roles padrão (user, manager, admin)
- Usuário admin padrão

Este script deve ser executado uma única vez após criar as tabelas.
"""

import json
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine, Base
from app.models.user import Role, User
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)


def create_default_roles(db: Session):
    """Cria as roles padrão do sistema."""

    roles_data = [
        {
            "name": "user",
            "description": "Usuário comum com permissões básicas",
            "permissions": [
                "users:read_own",
                "orders:read",
                "orders:create",
                "products:read",
                "categories:read",
                "stock:read",
                "clients:read",
                "addresses:read"
            ]
        },
        {
            "name": "manager",
            "description": "Gerente com permissões de gerenciamento",
            "permissions": [
                "users:read",
                "users:write",
                "orders:read",
                "orders:write",
                "reports:read",
                "products:read",
                "products:write",
                "categories:read",
                "categories:write",
                "stock:read",
                "stock:write",
                "clients:read",
                "clients:write",
                "addresses:read",
                "addresses:write"
            ]
        },
        {
            "name": "admin",
            "description": "Administrador com permissões totais",
            "permissions": [
                "users:read",
                "users:write",
                "users:delete",
                "roles:read",
                "roles:write",
                "roles:delete",
                "orders:read",
                "orders:write",
                "orders:delete",
                "products:read",
                "products:write",
                "products:delete",
                "categories:read",
                "categories:write",
                "stock:read",
                "stock:write",
                "reports:read",
                "reports:write",
                "settings:write",
                "clients:read",
                "clients:write",
                "clients:delete",
                "addresses:read",
                "addresses:write",
                "addresses:delete"
            ]
        }
    ]

    for role_data in roles_data:
        # Verificar se role já existe
        existing = db.query(Role).filter(Role.name == role_data["name"]).first()
        if existing:
            logger.info(f"Role '{role_data['name']}' já existe, pulando...")
            continue

        role = Role(
            name=role_data["name"],
            description=role_data["description"],
            permissions=json.dumps(role_data["permissions"]),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(role)
        logger.info(f"Criada role: {role_data['name']}")

    db.commit()


def create_default_admin(db: Session):
    """Cria o usuário admin padrão."""

    admin_email = "admin@sistema-vendas.local"

    # Verificar se admin já existe
    existing = db.query(User).filter(User.email == admin_email).first()
    if existing:
        logger.info("Usuário admin já existe, pulando...")
        return

    # Obter a role 'admin'
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        logger.error("Role 'admin' não encontrada. Certifique-se de criar as roles primeiro.")
        return

    # Criar usuário admin
    hashed_password = AuthService.hash_password("Admin@123")
    admin_user = User(
        email=admin_email,
        hashed_password=hashed_password,
        first_name="Administrador",
        last_name="Sistema",
        role_id=admin_role.id,
        active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(admin_user)
    db.commit()
    logger.info(f"Criado usuário admin: {admin_email} (senha: Admin@123)")


def init_db():
    """
    Inicializa o banco de dados com dados padrão.
    Deve ser chamado após a criação das tabelas com Alembic.
    """
    logger.info("Iniciando seed de dados...")

    # Criar todas as tabelas (se ainda não existirem)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        create_default_roles(db)
        create_default_admin(db)
        logger.info("Seed de dados concluído com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao fazer seed de dados: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Configure logging se executado como script
    import sys
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    init_db()
