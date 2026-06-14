"""
Serviço de autenticação.

Responsável por:
- Registro de usuários
- Login e geração de tokens JWT
- Refresh de access_token
- Recuperação de senha (forgot/reset)
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User, Role
from app.repositories.user_repository import UserRepository
from app.repositories.password_reset_repository import PasswordResetRepository
from app.repositories.role_repository import RoleRepository
from app.schemas.auth import Token
from app.utils.email import send_password_reset_email

logger = logging.getLogger(__name__)

# Contexto bcrypt para hashing de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Serviço centralizado de autenticação e autorização."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash de uma senha com bcrypt."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica se a senha em texto plano corresponde ao hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(user_id: int) -> tuple[str, datetime]:
        """
        Cria um JWT access_token com validade de 1 hora.
        Retorna (token, expires_at).
        """
        expires_at = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(user_id),
            "exp": expires_at,
            "type": "access"
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return token, expires_at

    @staticmethod
    def create_refresh_token(user_id: int) -> tuple[str, datetime]:
        """
        Cria um JWT refresh_token com validade de 7 dias.
        Retorna (token, expires_at).
        """
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            "sub": str(user_id),
            "exp": expires_at,
            "type": "refresh"
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return token, expires_at

    @staticmethod
    def register(db: Session, email: str, password: str, first_name: str, last_name: str) -> Optional[User]:
        """
        Registro de novo usuário.
        O novo usuário recebe a role padrão (a de menor ID, geralmente 'user').
        """
        # Verificar se email já existe
        existing_user = UserRepository.get_by_email(db, email)
        if existing_user:
            logger.warning(f"Tentativa de registro com email já existente: {email}")
            return None

        # Obter a role padrão (primeira role, geralmente 'user')
        default_role = db.query(Role).order_by(Role.id).first()
        if not default_role:
            logger.error("Nenhuma role padrão encontrada no banco de dados")
            return None

        hashed_password = AuthService.hash_password(password)

        user = UserRepository.create(
            db=db,
            email=email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            role_id=default_role.id
        )

        logger.info(f"Novo usuário registrado: {email}")
        return user

    @staticmethod
    def login(db: Session, email: str, password: str) -> Optional[Token]:
        """
        Login de usuário e geração de tokens JWT.
        Retorna None se credenciais inválidas ou usuário inativo.
        """
        user = UserRepository.get_by_email_and_active(db, email)

        if not user:
            logger.warning(f"Tentativa de login com email inválido ou inativo: {email}")
            return None

        if not AuthService.verify_password(password, user.hashed_password):
            logger.warning(f"Tentativa de login com senha incorreta: {email}")
            return None

        access_token, access_expires_at = AuthService.create_access_token(user.id)
        refresh_token, refresh_expires_at = AuthService.create_refresh_token(user.id)

        # Calcular tempo de expiração do access_token em segundos
        expires_in = int((access_expires_at - datetime.utcnow()).total_seconds())

        logger.info(f"Usuário autenticado com sucesso: {email}")
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in
        )

    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> Optional[Token]:
        """
        Gera um novo access_token a partir de um refresh_token válido.
        """
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except JWTError:
            logger.warning("Tentativa de refresh com token inválido")
            return None

        # Verificar se é realmente um refresh_token
        if payload.get("type") != "refresh":
            logger.warning("Tentativa de refresh com token de tipo incorreto")
            return None

        user_id = int(payload.get("sub"))
        user = UserRepository.get_by_id(db, user_id)

        if not user or not user.active:
            logger.warning(f"Tentativa de refresh para usuário inválido ou inativo: {user_id}")
            return None

        access_token, access_expires_at = AuthService.create_access_token(user.id)
        new_refresh_token, _ = AuthService.create_refresh_token(user.id)

        expires_in = int((access_expires_at - datetime.utcnow()).total_seconds())

        logger.info(f"Access token renovado para usuário: {user.email}")
        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=expires_in
        )

    @staticmethod
    def verify_access_token(token: str) -> Optional[int]:
        """
        Verifica e decodifica um access_token, retornando o user_id.
        Retorna None se token inválido ou expirado.
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except JWTError:
            logger.debug("Token JWT inválido ou expirado")
            return None

        # Verificar se é um access_token
        if payload.get("type") != "access":
            logger.debug("Token não é um access_token válido")
            return None

        user_id = payload.get("sub")
        if not user_id:
            logger.debug("User ID não encontrado no token")
            return None

        return int(user_id)

    @staticmethod
    def request_password_reset(db: Session, email: str) -> bool:
        """
        Inicia processo de reset de senha.
        Cria token e envia email.
        """
        user = UserRepository.get_by_email(db, email)
        if not user:
            # Não revelamos se email existe ou não
            logger.debug(f"Requisição de reset para email não encontrado: {email}")
            return True

        # Gerar token com validade de 30 minutos
        token, expires_at = AuthService.create_access_token(user.id)
        # Usar um token diferente (baseado no JTI) para maior segurança
        # Aqui simplificamos usando o mesmo JWT mas poderia ser um token separado
        import secrets
        reset_token = secrets.token_urlsafe(32)

        PasswordResetRepository.create(
            db=db,
            user_id=user.id,
            token=reset_token,
            expires_at=datetime.utcnow() + timedelta(minutes=30)
        )

        # Enviar email com token
        send_password_reset_email(user.email, user.first_name, reset_token)

        logger.info(f"Requisição de reset de senha enviada para: {email}")
        return True

    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> Optional[User]:
        """
        Conclui o reset de senha usando o token.
        """
        password_reset = PasswordResetRepository.get_by_token(db, token)

        if not password_reset:
            logger.warning("Tentativa de reset com token inválido")
            return None

        if password_reset.expired:
            logger.warning("Tentativa de reset com token já utilizado")
            return None

        if password_reset.expires_at < datetime.utcnow():
            logger.warning("Tentativa de reset com token expirado")
            PasswordResetRepository.mark_as_expired(db, password_reset.id)
            return None

        # Atualizar senha e marcar token como usado
        hashed_password = AuthService.hash_password(new_password)
        user = UserRepository.update_password(db, password_reset.user_id, hashed_password)

        PasswordResetRepository.mark_as_expired(db, password_reset.id)

        logger.info(f"Senha resetada com sucesso para usuário: {user.email}")
        return user
