"""
Router de autenticação.

Endpoints:
- POST /auth/register: Registro público de novo usuário
- POST /auth/login: Login e obtenção de tokens
- POST /auth/refresh: Refresh do access_token
- POST /auth/forgot-password: Solicitação de reset de senha
- POST /auth/reset-password: Confirmação de reset com novo token
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import Token, RefreshTokenRequest, ForgotPasswordRequest, ResetPasswordRequest
from app.schemas.user import UserCreate, UserOut
from app.services.auth_service import AuthService
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["autenticação"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Registro público de novo usuário.
    A senha deve ter no mínimo 8 caracteres.
    O novo usuário recebe automaticamente a role padrão (user).
    """
    user = AuthService.register(
        db=db,
        email=user_data.email,
        password=user_data.password,
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já registrado ou erro ao criar usuário"
        )

    return user


@router.post("/login", response_model=Token)
def login(
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    """
    Autenticação de usuário.
    Retorna access_token (válido por 1h) e refresh_token (válido por 7 dias).
    """
    token = AuthService.login(db, email, password)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )

    return token


@router.post("/refresh", response_model=Token)
def refresh(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Renova o access_token usando um refresh_token válido.
    Retorna novo access_token e novo refresh_token.
    """
    token = AuthService.refresh_access_token(db, request.refresh_token)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado"
        )

    return token


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Solicita reset de senha.
    Envia um email com link de reset (válido por 30 minutos).
    Não revela se o email existe ou não no sistema.
    """
    AuthService.request_password_reset(db, request.email)
    return {"message": "Se o email existir, um link de reset será enviado"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Conclui o reset de senha usando o token enviado por email.
    """
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senhas não correspondem"
        )

    user = AuthService.reset_password(db, request.token, request.new_password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido, expirado ou já utilizado"
        )

    return {"message": "Senha resetada com sucesso"}
