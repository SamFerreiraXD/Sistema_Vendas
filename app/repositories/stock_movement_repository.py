"""
Repository para operações da tabela StockMovement.
"""

from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.product import StockMovement


class StockMovementRepository:
    """Data access layer para StockMovement."""

    @staticmethod
    def create(db: Session, product_id: int, type: str, quantity: int, reason: str, user_id: int) -> StockMovement:
        """
        Registra uma nova movimentação de estoque.
        
        Args:
            product_id: ID do produto
            type: "in" ou "out"
            quantity: Quantidade (sempre positiva, o tipo define direção)
            reason: Motivo da movimentação
            user_id: ID do usuário que fez a operação
        """
        movement = StockMovement(
            product_id=product_id,
            type=type,
            quantity=quantity,
            reason=reason,
            user_id=user_id
        )
        db.add(movement)
        db.commit()
        db.refresh(movement)
        return movement

    @staticmethod
    def get_by_id(db: Session, movement_id: int) -> Optional[StockMovement]:
        """Retorna uma movimentação por ID."""
        return db.query(StockMovement).filter(StockMovement.id == movement_id).first()

    @staticmethod
    def get_by_product(db: Session, product_id: int, limit: int = 50) -> List[StockMovement]:
        """Retorna o histórico de movimentação de um produto."""
        return db.query(StockMovement).filter(
            StockMovement.product_id == product_id
        ).order_by(StockMovement.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_by_date_range(db: Session, product_id: int, start_date: datetime, end_date: datetime) -> List[StockMovement]:
        """Retorna movimentações de um produto em um período."""
        return db.query(StockMovement).filter(
            StockMovement.product_id == product_id,
            StockMovement.created_at >= start_date,
            StockMovement.created_at <= end_date
        ).order_by(StockMovement.created_at.desc()).all()

    @staticmethod
    def get_by_type(db: Session, product_id: int, type: str) -> List[StockMovement]:
        """Retorna todas as movimentações de entrada ou saída."""
        return db.query(StockMovement).filter(
            StockMovement.product_id == product_id,
            StockMovement.type == type
        ).order_by(StockMovement.created_at.desc()).all()

    @staticmethod
    def get_total_in(db: Session, product_id: int) -> int:
        """Calcula o total de entradas de um produto."""
        result = db.query(StockMovement).filter(
            StockMovement.product_id == product_id,
            StockMovement.type == "in"
        ).all()
        return sum(m.quantity for m in result)

    @staticmethod
    def get_total_out(db: Session, product_id: int) -> int:
        """Calcula o total de saídas de um produto."""
        result = db.query(StockMovement).filter(
            StockMovement.product_id == product_id,
            StockMovement.type == "out"
        ).all()
        return sum(m.quantity for m in result)

    @staticmethod
    def get_recent(db: Session, days: int = 30, limit: int = 100) -> List[StockMovement]:
        """Retorna as movimentações mais recentes."""
        start_date = datetime.utcnow() - timedelta(days=days)
        return db.query(StockMovement).filter(
            StockMovement.created_at >= start_date
        ).order_by(StockMovement.created_at.desc()).limit(limit).all()
