"""
Router de produtos.

Endpoints:
- GET /products: Listar todos os produtos com filtros
- GET /products/{product_id}: Obter detalhes de um produto
- GET /products/search: Buscar produtos por nome
- GET /products/category/{category_id}: Produtos de uma categoria
- GET /products/low-stock: Produtos com estoque baixo
- POST /products: Criar novo produto (requer 'products:write')
- PUT /products/{product_id}: Atualizar produto (requer 'products:write')
- DELETE /products/{product_id}: Desativar produto (requer 'products:delete')
- POST /products/{product_id}/activate: Ativar produto desativado (requer 'products:write')
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user, require_permission
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut
from app.services.product_service import ProductService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["produtos"])


@router.get("", response_model=list[ProductOut])
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(require_permission("products:read"))
):
    """
    Lista todos os produtos ativos.
    Requer permissão 'products:read'.
    """
    products = ProductService.get_all_products(db, active_only=True)
    return products[skip : skip + limit]


@router.get("/search", response_model=list[ProductOut])
def search_products(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(require_permission("products:read"))
):
    """
    Busca produtos por nome (LIKE).
    Requer permissão 'products:read'.
    """
    products = ProductService.search_products(db, q)
    return products


@router.get("/category/{category_id}", response_model=list[ProductOut])
def get_products_by_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(require_permission("products:read"))
):
    """
    Retorna todos os produtos de uma categoria.
    Requer permissão 'products:read'.
    """
    products = ProductService.get_products_by_category(db, category_id)
    return products


@router.get("/low-stock", response_model=list[ProductOut])
def get_low_stock_products(
    threshold: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(require_permission("products:read"))
):
    """
    Retorna produtos com estoque abaixo do limite especificado.
    Requer permissão 'products:read'.
    """
    products = ProductService.get_low_stock_products(db, threshold)
    return products


@router.get("/{product_id}", response_model=ProductOut)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(require_permission("products:read"))
):
    """
    Obtém detalhes de um produto específico.
    Requer permissão 'products:read'.
    """
    product = ProductService.get_product_by_id(db, product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )

    return product


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(require_permission("products:write"))
):
    """
    Cria um novo produto.
    Requer permissão 'products:write'.
    Valida SKU e código de barras únicos.
    """
    product = ProductService.create_product(
        db,
        category_id=product_data.category_id,
        name=product_data.name,
        description=product_data.description,
        sku=product_data.sku,
        barcode=product_data.barcode,
        price_cost=product_data.price_cost,
        price_sale=product_data.price_sale
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao criar produto. Verifique se SKU, código de barras ou categoria são válidos."
        )

    return product


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(require_permission("products:write"))
):
    """
    Atualiza dados de um produto.
    Requer permissão 'products:write'.
    """
    product = ProductService.update_product(
        db,
        product_id,
        category_id=product_data.category_id,
        name=product_data.name,
        description=product_data.description,
        sku=product_data.sku,
        barcode=product_data.barcode,
        price_cost=product_data.price_cost,
        price_sale=product_data.price_sale,
        active=product_data.active
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )

    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(require_permission("products:delete"))
):
    """
    Desativa um produto (soft delete).
    Requer permissão 'products:delete'.
    """
    product = ProductService.deactivate_product(db, product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )

    return None


@router.post("/{product_id}/activate", response_model=ProductOut)
def activate_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(require_permission("products:write"))
):
    """
    Ativa um produto desativado.
    Requer permissão 'products:write'.
    """
    product = ProductService.activate_product(db, product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )

    return product
