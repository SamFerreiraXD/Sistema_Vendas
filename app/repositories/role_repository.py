"""
Repository para operações CRUD da tabela Role.
"""

import json
from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.user import Role


class RoleRepository:
    """Data access layer para Role."""

    @staticmethod
    def get_all(db: Session) -> List[Role]:
        """Retorna todas as roles."""
        return db.query(Role).all()

    @staticmethod
    def get_by_id(db: Session, role_id: int) -> Optional[Role]:
        """Retorna uma role por ID."""
        return db.query(Role).filter(Role.id == role_id).first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Role]:
        """Retorna uma role por nome."""
        return db.query(Role).filter(Role.name == name).first()

    @staticmethod
    def create(db: Session, name: str, description: Optional[str] = None, permissions: List[str] = None) -> Role:
        """Cria uma nova role."""
        if permissions is None:
            permissions = []

        permissions_json = json.dumps(permissions)
        role = Role(
            name=name,
            description=description,
            permissions=permissions_json
        )
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

    @staticmethod
    def update(db: Session, role_id: int, name: Optional[str] = None,
               description: Optional[str] = None, permissions: Optional[List[str]] = None) -> Optional[Role]:
        """Atualiza uma role."""
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            return None

        if name is not None:
            role.name = name
        if description is not None:
            role.description = description
        if permissions is not None:
            role.permissions = json.dumps(permissions)

        db.commit()
        db.refresh(role)
        return role

    @staticmethod
    def delete(db: Session, role_id: int) -> bool:
        """Deleta uma role (e seus usuários se houver cascade)."""
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            return False

        db.delete(role)
        db.commit()
        return True

    @staticmethod
    def get_permissions(db: Session, role_id: int) -> List[str]:
        """Retorna a lista de permissões de uma role."""
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            return []

        try:
            return json.loads(role.permissions)
        except (json.JSONDecodeError, TypeError):
            return []
