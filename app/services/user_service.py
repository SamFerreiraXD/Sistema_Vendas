"""
Serviço de gerenciamento de usuários.

Responsável por:
- CRUD de usuários
- Mudança de senha
- Ativação/desativação
"""

import logging
from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)


class UserService:
    """Serviço de gerenciamento de usuários."""

    @staticmethod
    def get_all_users(db: Session, active_only: bool = True) -> List[User]:
        """Retorna todos os usuários."""
        return UserRepository.get_all(db, active_only=active_only)

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Retorna um usuário por ID."""
        return UserRepository.get_by_id(db, user_id)

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Retorna um usuário por email."""
        return UserRepository.get_by_email(db, email)

    @staticmethod
    def create_user(db: Session, email: str, password: str, first_name: str,
                    last_name: str, role_id: int) -> Optional[User]:
        """
        Cria um novo usuário com role específica.
        Usado apenas pelo endpoint /users que requer permissão 'users:write'.
        """
        # Verificar se email já existe
        existing_user = UserRepository.get_by_email(db, email)
        if existing_user:
            logger.warning(f"Tentativa de criar usuário com email já existente: {email}")
            return None

        hashed_password = AuthService.hash_password(password)

        user = UserRepository.create(
            db=db,
            email=email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            role_id=role_id
        )

        logger.info(f"Novo usuário criado: {email} com role_id: {role_id}")
        return user

    @staticmethod
    def update_user(db: Session, user_id: int, first_name: Optional[str] = None,
                    last_name: Optional[str] = None, active: Optional[bool] = None) -> Optional[User]:
        """Atualiza dados de um usuário."""
        user = UserRepository.update(db, user_id, first_name, last_name, active)

        if user:
            logger.info(f"Usuário atualizado: {user.email}")
        else:
            logger.warning(f"Tentativa de atualizar usuário inexistente: {user_id}")

        return user

    @staticmethod
    def change_password(db: Session, user_id: int, current_password: str, new_password: str) -> bool:
        """
        Altera a senha do usuário após validar a senha atual.
        """
        user = UserRepository.get_by_id(db, user_id)

        if not user:
            logger.warning(f"Tentativa de alterar senha de usuário inexistente: {user_id}")
            return False

        if not AuthService.verify_password(current_password, user.hashed_password):
            logger.warning(f"Tentativa de alterar senha com senha atual incorreta: {user.email}")
            return False

        hashed_password = AuthService.hash_password(new_password)
        UserRepository.update_password(db, user_id, hashed_password)

        logger.info(f"Senha alterada com sucesso: {user.email}")
        return True

    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> Optional[User]:
        """Desativa um usuário (soft delete)."""
        user = UserRepository.deactivate(db, user_id)

        if user:
            logger.info(f"Usuário desativado: {user.email}")
        else:
            logger.warning(f"Tentativa de desativar usuário inexistente: {user_id}")

        return user

    @staticmethod
    def activate_user(db: Session, user_id: int) -> Optional[User]:
        """Ativa um usuário desativado."""
        user = UserRepository.activate(db, user_id)

        if user:
            logger.info(f"Usuário ativado: {user.email}")
        else:
            logger.warning(f"Tentativa de ativar usuário inexistente: {user_id}")

        return user
