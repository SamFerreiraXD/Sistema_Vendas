"""
Repository para operações da tabela PasswordReset.
"""

from typing import Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.user import PasswordReset


class PasswordResetRepository:
    """Data access layer para PasswordReset."""

    @staticmethod
    def create(db: Session, user_id: int, token: str, expires_at: datetime) -> PasswordReset:
        """Cria uma nova requisição de reset de senha."""
        password_reset = PasswordReset(
            user_id=user_id,
            token=token,
            expired=False,
            expires_at=expires_at
        )
        db.add(password_reset)
        db.commit()
        db.refresh(password_reset)
        return password_reset

    @staticmethod
    def get_by_token(db: Session, token: str) -> Optional[PasswordReset]:
        """Retorna uma requisição de reset pelo token."""
        return db.query(PasswordReset).filter(PasswordReset.token == token).first()

    @staticmethod
    def mark_as_expired(db: Session, reset_id: int) -> Optional[PasswordReset]:
        """Marca uma requisição de reset como expirada."""
        password_reset = db.query(PasswordReset).filter(PasswordReset.id == reset_id).first()
        if not password_reset:
            return None

        password_reset.expired = True
        db.commit()
        db.refresh(password_reset)
        return password_reset

    @staticmethod
    def get_by_user_id_active(db: Session, user_id: int) -> Optional[PasswordReset]:
        """Retorna a requisição de reset ativa mais recente do usuário."""
        return db.query(PasswordReset).filter(
            PasswordReset.user_id == user_id,
            PasswordReset.expired == False,
            PasswordReset.expires_at > datetime.utcnow()
        ).order_by(PasswordReset.created_at.desc()).first()

    @staticmethod
    def delete(db: Session, reset_id: int) -> bool:
        """Deleta uma requisição de reset."""
        password_reset = db.query(PasswordReset).filter(PasswordReset.id == reset_id).first()
        if not password_reset:
            return False

        db.delete(password_reset)
        db.commit()
        return True
