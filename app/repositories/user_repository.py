"""
Repository para operações CRUD da tabela User.
"""

from typing import Optional, List

from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

from app.models.user import User


class UserRepository:
    """Data access layer para User."""

    @staticmethod
    def get_all(db: Session, active_only: bool = True) -> List[User]:
        """
        Retorna todos os usuários.
        Usa joinedload para evitar N+1 ao carregar a Role.
        """
        query = db.query(User).options(joinedload(User.role))
        if active_only:
            query = query.filter(User.active == True)
        return query.all()

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """Retorna um usuário por ID (carrega Role com joinedload)."""
        return db.query(User).options(joinedload(User.role)).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """Retorna um usuário por email (carrega Role com joinedload)."""
        return db.query(User).options(joinedload(User.role)).filter(User.email == email).first()

    @staticmethod
    def get_by_email_and_active(db: Session, email: str) -> Optional[User]:
        """Retorna um usuário ativo por email."""
        return db.query(User).options(joinedload(User.role)).filter(
            and_(User.email == email, User.active == True)
        ).first()

    @staticmethod
    def create(db: Session, email: str, hashed_password: str, first_name: str,
               last_name: str, role_id: int) -> User:
        """Cria um novo usuário."""
        user = User(
            email=email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            role_id=role_id,
            active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        # Recarregar com joinedload para obter a Role
        return db.query(User).options(joinedload(User.role)).filter(User.id == user.id).first()

    @staticmethod
    def update(db: Session, user_id: int, first_name: Optional[str] = None,
               last_name: Optional[str] = None, active: Optional[bool] = None) -> Optional[User]:
        """Atualiza dados de um usuário."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if active is not None:
            user.active = active

        db.commit()
        db.refresh(user)
        # Recarregar com joinedload
        return db.query(User).options(joinedload(User.role)).filter(User.id == user.id).first()

    @staticmethod
    def update_password(db: Session, user_id: int, hashed_password: str) -> Optional[User]:
        """Atualiza a senha de um usuário."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        user.hashed_password = hashed_password
        db.commit()
        db.refresh(user)
        return db.query(User).options(joinedload(User.role)).filter(User.id == user.id).first()

    @staticmethod
    def deactivate(db: Session, user_id: int) -> Optional[User]:
        """Desativa um usuário (soft delete)."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        user.active = False
        db.commit()
        db.refresh(user)
        return db.query(User).options(joinedload(User.role)).filter(User.id == user.id).first()

    @staticmethod
    def activate(db: Session, user_id: int) -> Optional[User]:
        """Ativa um usuário desativado."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        user.active = True
        db.commit()
        db.refresh(user)
        return db.query(User).options(joinedload(User.role)).filter(User.id == user.id).first()
