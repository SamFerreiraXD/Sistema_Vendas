"""
Router de categorias.

Endpoints:
- GET /categories: Listar todas as categorias
- GET /categories/{category_id}: Obter detalhes de uma categoria
- POST /categories: Criar nova categoria (requer permissão 'categories:write')
- PUT /categories/{category_id}: Atualizar categoria (requer permissão 'categories:write')
- DELETE /categories/{category_id}: Deletar categoria (requer permissão 'categories:write')
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user, require_permission
from app.models.user import User
from app.schemas.product import CategoryCreate, CategoryOut
from app.services.product_service import CategoryService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/categories", tags=["categorias"])


@router.get("", response_model=list[CategoryOut])
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(require_permission("categories:read"))
):
    """
    Lista todas as categorias de produtos.
    Requer permissão 'categories:read'.
    """
    categories = CategoryService.get_all_categories(db)
    return categories


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(require_permission("categories:read"))
):
    """
    Obtém detalhes de uma categoria específica.
    Requer permissão 'categories:read'.
    """
    category = CategoryService.get_category_by_id(db, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada"
        )

    return category


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(require_permission("categories:write"))
):
    """
    Cria uma nova categoria de produtos.
    Requer permissão 'categories:write'.
    """
    category = CategoryService.create_category(
        db,
        name=category_data.name,
        slug=category_data.slug,
        description=category_data.description
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao criar categoria. Verifique se nome e slug já não existem."
        )

    return category


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(require_permission("categories:write"))
):
    """
    Atualiza uma categoria existente.
    Requer permissão 'categories:write'.
    """
    category = CategoryService.update_category(
        db,
        category_id,
        name=category_data.name,
        slug=category_data.slug,
        description=category_data.description
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada"
        )

    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(require_permission("categories:write"))
):
    """
    Deleta uma categoria.
    Requer permissão 'categories:write'.
    """
    success = CategoryService.delete_category(db, category_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada"
        )

    return None
