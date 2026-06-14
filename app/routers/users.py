"""
Router de gerenciamento de usuários.

Endpoints:
- GET /users: Listar todos os usuários (requer permissão 'users:read')
- GET /users/{user_id}: Obter dados de um usuário
- GET /users/me: Obter dados do usuário autenticado
- POST /users: Criar novo usuário (requer permissão 'users:write')
- PUT /users/{user_id}: Atualizar dados de usuário (requer permissão 'users:write')
- POST /users/{user_id}/change-password: Alterar senha do próprio usuário
- DELETE /users/{user_id}: Desativar usuário (requer permissão 'users:write')
- POST /users/{user_id}/activate: Ativar usuário (requer permissão 'users:write')
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user, require_permission
from app.models.user import User
from app.schemas.user import UserCreateWithRole, UserUpdate, UserOut, ChangePasswordRequest
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["usuários"])


@router.get("", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(require_permission("users:read"))
):
    """
    Lista todos os usuários ativos.
    Requer permissão 'users:read'.
    """
    users = UserService.get_all_users(db, active_only=True)
    return users


@router.get("/me", response_model=UserOut)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Retorna os dados do usuário autenticado.
    """
    return current_user


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtém dados de um usuário específico.
    Usuários comuns só podem ver seus próprios dados.
    Usuários com permissão 'users:read' podem ver qualquer um.
    """
    # Se o ID não é do próprio usuário, verificar permissão
    if user_id != current_user.id:
        # Verificar se tem permissão (simplificado - poderia usar require_permission)
        from app.utils.permissions import parse_permissions, has_permission
        user_permissions = parse_permissions(current_user.role.permissions)
        if not has_permission(user_permissions, "users:read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar dados de outros usuários"
            )

    user = UserService.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    return user


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreateWithRole,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(require_permission("users:write"))
):
    """
    Cria um novo usuário com role específica.
    Requer permissão 'users:write'.
    Diferente do /auth/register, este endpoint aceita role_id.
    """
    user = UserService.create_user(
        db=db,
        email=user_data.email,
        password=user_data.password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role_id=user_data.role_id
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já registrado ou role_id inválido"
        )

    return user


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(require_permission("users:write"))
):
    """
    Atualiza dados de um usuário.
    Requer permissão 'users:write'.
    """
    user = UserService.update_user(
        db=db,
        user_id=user_id,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        active=user_data.active
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    return user


@router.post("/{user_id}/change-password", status_code=status.HTTP_200_OK)
def change_password(
    user_id: int,
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Altera a senha do usuário autenticado.
    Usuários só podem alterar sua própria senha.
    Admins com permissão especial poderiam alterar outras senhas.
    """
    # Usuário comum só pode alterar sua própria senha
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode alterar sua própria senha"
        )

    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senhas não correspondem"
        )

    success = UserService.change_password(
        db=db,
        user_id=user_id,
        current_password=request.current_password,
        new_password=request.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta ou erro ao alterar senha"
        )

    return {"message": "Senha alterada com sucesso"}


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(require_permission("users:write"))
):
    """
    Desativa um usuário (soft delete).
    Requer permissão 'users:write'.
    """
    user = UserService.deactivate_user(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    return None


@router.post("/{user_id}/activate", response_model=UserOut)
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(require_permission("users:write"))
):
    """
    Ativa um usuário desativado.
    Requer permissão 'users:write'.
    """
    user = UserService.activate_user(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    return user
