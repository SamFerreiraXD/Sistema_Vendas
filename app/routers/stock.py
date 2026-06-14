"""
Router de estoque.

Endpoints:
- GET /stock/{product_id}: Obter informações de estoque de um produto
- GET /stock/{product_id}/history: Histórico de movimentação de um produto
- POST /stock/movement: Registrar entrada ou saída de estoque
- GET /stock/check/{product_id}: Verificar disponibilidade (query param: quantity)
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user, require_permission
from app.models.user import User
from app.schemas.product import StockMovementCreate, StockMovementOut
from app.services.stock_service import StockService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stock", tags=["estoque"])


@router.get("/{product_id}", response_model=dict)
def get_stock_info(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(require_permission("stock:read"))
):
    """
    Retorna informações de estoque de um produto.
    Requer permissão 'stock:read'.
    """
    stock_info = StockService.get_stock_totals(db, product_id)

    if not stock_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )

    return stock_info


@router.get("/{product_id}/history", response_model=list[StockMovementOut])
def get_stock_history(
    product_id: int,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(require_permission("stock:read"))
):
    """
    Retorna o histórico de movimentação de estoque de um produto.
    Requer permissão 'stock:read'.
    """
    movements = StockService.get_product_stock_history(db, product_id, limit)
    return movements


@router.post("/movement", response_model=StockMovementOut, status_code=status.HTTP_201_CREATED)
def register_stock_movement(
    movement_data: StockMovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(require_permission("stock:write"))
):
    """
    Registra uma movimentação de estoque (entrada ou saída).
    Requer permissão 'stock:write'.
    
    Para entradas (type="in"):
    - Adiciona quantidade ao estoque
    
    Para saídas (type="out"):
    - Valida disponibilidade
    - Remove quantidade do estoque
    """
    if movement_data.type == "in":
        movement = StockService.add_stock(
            db,
            product_id=movement_data.product_id,
            quantity=movement_data.quantity,
            reason=movement_data.reason,
            user_id=current_user.id
        )
    elif movement_data.type == "out":
        movement = StockService.remove_stock(
            db,
            product_id=movement_data.product_id,
            quantity=movement_data.quantity,
            reason=movement_data.reason,
            user_id=current_user.id
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de movimentação inválido. Use 'in' ou 'out'."
        )

    if not movement:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao registrar movimentação. Verifique o produto ou estoque insuficiente."
        )

    return movement


@router.get("/check/{product_id}")
def check_stock_availability(
    product_id: int,
    quantity: int = Query(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(require_permission("stock:read"))
):
    """
    Verifica se há quantidade suficiente de um produto em estoque.
    Requer permissão 'stock:read'.
    
    Query params:
    - quantity: quantidade a verificar
    """
    available = StockService.check_availability(db, product_id, quantity)
    current = StockService.get_current_stock(db, product_id)

    if current is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )

    return {
        "product_id": product_id,
        "requested_quantity": quantity,
        "current_stock": current,
        "available": available
    }
