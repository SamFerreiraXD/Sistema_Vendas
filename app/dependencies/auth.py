"""
Dependências de autenticação e autorização para FastAPI.

Fornece:
- get_current_user: Dependency que extrai e valida o token JWT
- require_permission: Dependency factory que valida permissões
"""

import logging
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.utils.permissions import parse_permissions, has_permission

logger = logging.getLogger(__name__)

# Esquema HTTP Bearer para extrair o token do header Authorization
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency que extrai e valida o JWT do header Authorization.
    Retorna o User se válido, caso contrário lança HTTPException 401.

    Uso:
        @router.get("/me")
        def get_me(current_user: User = Depends(get_current_user)):
            return current_user
    """
    token = credentials.credentials

    # Verificar e decodificar o token
    user_id = AuthService.verify_access_token(token)

    if not user_id:
        logger.warning("Tentativa de acesso com token inválido ou expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Buscar o usuário no banco
    user = UserRepository.get_by_id(db, user_id)

    if not user or not user.active:
        logger.warning(f"Tentativa de acesso com usuário inválido ou inativo: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou desativado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_permission(required_permission: str):
    """
    Dependency factory que valida se o usuário tem uma permissão específica.
    Retorna um decorator que pode ser usado junto com get_current_user.

    Uso:
        @router.post("/users")
        def create_user(
            user_data: UserCreateWithRole,
            current_user: User = Depends(get_current_user),
            _ = Depends(require_permission("users:write"))
        ):
            return create_user_impl(user_data)
    """

    async def check_permission(current_user: User = Depends(get_current_user)) -> User:
        """
        Verifica se o usuário tem a permissão requerida.
        """
        # Parsear as permissões do role do usuário
        user_permissions = parse_permissions(current_user.role.permissions)

        if not has_permission(user_permissions, required_permission):
            logger.warning(
                f"Acesso negado para usuário {current_user.email}: "
                f"permissão '{required_permission}' não encontrada"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão '{required_permission}' não autorizada",
            )

        return current_user

    return check_permission
