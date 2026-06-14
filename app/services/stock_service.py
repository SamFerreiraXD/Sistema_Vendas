"""
Serviço de gerenciamento de estoque.

Responsável por:
- Atualizar estoque (entradas e saídas)
- Validar disponibilidade antes de saídas
- Registrar histórico de movimentações
"""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.models.product import StockMovement
from app.repositories.product_repository import ProductRepository
from app.repositories.stock_movement_repository import StockMovementRepository

logger = logging.getLogger(__name__)


class StockService:
    """Serviço de gerenciamento de estoque."""

    @staticmethod
    def get_stock_movement_by_id(db: Session, movement_id: int) -> Optional[StockMovement]:
        """Retorna uma movimentação de estoque por ID."""
        return StockMovementRepository.get_by_id(db, movement_id)

    @staticmethod
    def get_product_stock_history(db: Session, product_id: int, limit: int = 50) -> list[StockMovement]:
        """Retorna o histórico de movimentação de um produto."""
        return StockMovementRepository.get_by_product(db, product_id, limit)

    @staticmethod
    def add_stock(db: Session, product_id: int, quantity: int, reason: str, user_id: int) -> Optional[StockMovement]:
        """
        Registra uma entrada de estoque.

        Args:
            product_id: ID do produto
            quantity: Quantidade a adicionar (deve ser positiva)
            reason: Motivo (ex: "Compra", "Devolução", "Ajuste")
            user_id: ID do usuário que fez a operação

        Returns:
            StockMovement se bem-sucedido, None caso contrário
        """
        if quantity <= 0:
            logger.warning(f"Tentativa de adicionar estoque com quantidade inválida: {quantity}")
            return None

        product = ProductRepository.get_by_id(db, product_id)
        if not product:
            logger.warning(f"Tentativa de adicionar estoque a produto inexistente: {product_id}")
            return None

        # Registrar movimentação
        movement = StockMovementRepository.create(
            db, product_id, "in", quantity, reason, user_id
        )

        # Atualizar estoque do produto
        ProductRepository.update_stock(db, product_id, quantity)

        logger.info(f"Estoque adicionado ao produto {product.sku}: +{quantity} ({reason})")
        return movement

    @staticmethod
    def remove_stock(db: Session, product_id: int, quantity: int, reason: str, user_id: int) -> Optional[StockMovement]:
        """
        Registra uma saída de estoque.
        Valida se há quantidade suficiente.

        Args:
            product_id: ID do produto
            quantity: Quantidade a remover (deve ser positiva)
            reason: Motivo (ex: "Venda", "Devolução", "Ajuste")
            user_id: ID do usuário que fez a operação

        Returns:
            StockMovement se bem-sucedido, None caso contrário
        """
        if quantity <= 0:
            logger.warning(f"Tentativa de remover estoque com quantidade inválida: {quantity}")
            return None

        product = ProductRepository.get_by_id(db, product_id)
        if not product:
            logger.warning(f"Tentativa de remover estoque de produto inexistente: {product_id}")
            return None

        # Validar disponibilidade
        if product.stock_quantity < quantity:
            logger.warning(
                f"Estoque insuficiente para produto {product.sku}: "
                f"disponível {product.stock_quantity}, solicitado {quantity}"
            )
            return None

        # Registrar movimentação
        movement = StockMovementRepository.create(
            db, product_id, "out", quantity, reason, user_id
        )

        # Atualizar estoque do produto (negativo para saída)
        ProductRepository.update_stock(db, product_id, -quantity)

        logger.info(f"Estoque removido do produto {product.sku}: -{quantity} ({reason})")
        return movement

    @staticmethod
    def get_current_stock(db: Session, product_id: int) -> int:
        """Retorna o estoque atual de um produto."""
        product = ProductRepository.get_by_id(db, product_id)
        if not product:
            return 0
        return product.stock_quantity

    @staticmethod
    def check_availability(db: Session, product_id: int, quantity: int) -> bool:
        """Verifica se há estoque suficiente de um produto."""
        product = ProductRepository.get_by_id(db, product_id)
        if not product:
            return False
        return product.stock_quantity >= quantity

    @staticmethod
    def get_stock_totals(db: Session, product_id: int) -> dict:
        """Retorna um resumo do estoque de um produto."""
        product = ProductRepository.get_by_id(db, product_id)
        if not product:
            return {}

        total_in = StockMovementRepository.get_total_in(db, product_id)
        total_out = StockMovementRepository.get_total_out(db, product_id)

        return {
            "product_id": product_id,
            "product_name": product.name,
            "product_sku": product.sku,
            "current_stock": product.stock_quantity,
            "total_in": total_in,
            "total_out": total_out,
            "expected_stock": total_in - total_out  # Para validação
        }
