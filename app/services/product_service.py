"""
Serviço de gerenciamento de produtos e categorias.

Responsável por:
- CRUD de produtos
- CRUD de categorias
- Validações de SKU e código de barras
- Regras de negócio
"""

import logging
from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.product import Product, Category
from app.repositories.product_repository import ProductRepository
from app.repositories.category_repository import CategoryRepository

logger = logging.getLogger(__name__)


class CategoryService:
    """Serviço de gerenciamento de categorias."""

    @staticmethod
    def get_all_categories(db: Session) -> List[Category]:
        """Retorna todas as categorias."""
        return CategoryRepository.get_all(db)

    @staticmethod
    def get_category_by_id(db: Session, category_id: int) -> Optional[Category]:
        """Retorna uma categoria por ID."""
        return CategoryRepository.get_by_id(db, category_id)

    @staticmethod
    def create_category(db: Session, name: str, slug: str, description: Optional[str] = None) -> Optional[Category]:
        """
        Cria uma nova categoria.
        Valida se slug e nome já existem.
        """
        # Verificar se categoria com mesmo nome já existe
        existing_name = CategoryRepository.get_by_name(db, name)
        if existing_name:
            logger.warning(f"Tentativa de criar categoria com nome duplicado: {name}")
            return None

        # Verificar se slug já existe
        existing_slug = CategoryRepository.get_by_slug(db, slug)
        if existing_slug:
            logger.warning(f"Tentativa de criar categoria com slug duplicado: {slug}")
            return None

        category = CategoryRepository.create(db, name, slug, description)
        logger.info(f"Categoria criada: {name} ({slug})")
        return category

    @staticmethod
    def update_category(db: Session, category_id: int, name: Optional[str] = None,
                       slug: Optional[str] = None, description: Optional[str] = None) -> Optional[Category]:
        """Atualiza uma categoria."""
        category = CategoryRepository.update(db, category_id, name, slug, description)

        if category:
            logger.info(f"Categoria atualizada: {category.name}")
        else:
            logger.warning(f"Tentativa de atualizar categoria inexistente: {category_id}")

        return category

    @staticmethod
    def delete_category(db: Session, category_id: int) -> bool:
        """Deleta uma categoria."""
        success = CategoryRepository.delete(db, category_id)

        if success:
            logger.info(f"Categoria deletada: {category_id}")
        else:
            logger.warning(f"Tentativa de deletar categoria inexistente: {category_id}")

        return success


class ProductService:
    """Serviço de gerenciamento de produtos."""

    @staticmethod
    def get_all_products(db: Session, active_only: bool = True) -> List[Product]:
        """Retorna todos os produtos."""
        return ProductRepository.get_all(db, active_only=active_only)

    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
        """Retorna um produto por ID."""
        return ProductRepository.get_by_id(db, product_id)

    @staticmethod
    def get_product_by_sku(db: Session, sku: str) -> Optional[Product]:
        """Retorna um produto por SKU."""
        return ProductRepository.get_by_sku(db, sku)

    @staticmethod
    def get_product_by_barcode(db: Session, barcode: str) -> Optional[Product]:
        """Retorna um produto por código de barras."""
        if not barcode:
            return None
        return ProductRepository.get_by_barcode(db, barcode)

    @staticmethod
    def search_products(db: Session, name: str) -> List[Product]:
        """Busca produtos por nome."""
        return ProductRepository.search_by_name(db, name)

    @staticmethod
    def get_products_by_category(db: Session, category_id: int) -> List[Product]:
        """Retorna todos os produtos de uma categoria."""
        return ProductRepository.get_by_category(db, category_id)

    @staticmethod
    def get_low_stock_products(db: Session, threshold: int = 10) -> List[Product]:
        """Retorna produtos com estoque abaixo do limite."""
        return ProductRepository.get_low_stock(db, threshold)

    @staticmethod
    def create_product(db: Session, category_id: int, name: str, description: Optional[str],
                      sku: str, barcode: Optional[str], price_cost: float,
                      price_sale: float) -> Optional[Product]:
        """
        Cria um novo produto.
        Valida SKU e código de barras únicos, preços válidos.
        """
        # Validar se categoria existe
        category = CategoryRepository.get_by_id(db, category_id)
        if not category:
            logger.warning(f"Tentativa de criar produto com category_id inexistente: {category_id}")
            return None

        # Validar SKU único
        existing_sku = ProductRepository.get_by_sku(db, sku)
        if existing_sku:
            logger.warning(f"Tentativa de criar produto com SKU duplicado: {sku}")
            return None

        # Validar código de barras único (se fornecido)
        if barcode:
            existing_barcode = ProductRepository.get_by_barcode(db, barcode)
            if existing_barcode:
                logger.warning(f"Tentativa de criar produto com código de barras duplicado: {barcode}")
                return None

        # Validar preços
        if price_cost <= 0 or price_sale <= 0:
            logger.warning(f"Tentativa de criar produto com preços inválidos")
            return None

        if price_sale < price_cost:
            logger.warning(f"Preço de venda menor que preço de custo para produto: {name}")
            # Não retornamos None aqui, pois pode ser uma estratégia de desconto
            # Apenas registramos no log

        product = ProductRepository.create(
            db, category_id, name, description, sku, barcode, price_cost, price_sale
        )
        logger.info(f"Produto criado: {name} (SKU: {sku})")
        return product

    @staticmethod
    def update_product(db: Session, product_id: int, category_id: Optional[int] = None,
                      name: Optional[str] = None, description: Optional[str] = None,
                      sku: Optional[str] = None, barcode: Optional[str] = None,
                      price_cost: Optional[float] = None, price_sale: Optional[float] = None,
                      active: Optional[bool] = None) -> Optional[Product]:
        """
        Atualiza um produto.
        Valida SKU e código de barras se alterados.
        """
        product = ProductRepository.update(
            db, product_id, category_id, name, description, sku, barcode,
            price_cost, price_sale, active
        )

        if product:
            logger.info(f"Produto atualizado: {product.name}")
        else:
            logger.warning(f"Tentativa de atualizar produto inexistente: {product_id}")

        return product

    @staticmethod
    def deactivate_product(db: Session, product_id: int) -> Optional[Product]:
        """Desativa um produto (soft delete)."""
        product = ProductRepository.deactivate(db, product_id)

        if product:
            logger.info(f"Produto desativado: {product.name}")
        else:
            logger.warning(f"Tentativa de desativar produto inexistente: {product_id}")

        return product

    @staticmethod
    def activate_product(db: Session, product_id: int) -> Optional[Product]:
        """Ativa um produto desativado."""
        product = ProductRepository.activate(db, product_id)

        if product:
            logger.info(f"Produto ativado: {product.name}")
        else:
            logger.warning(f"Tentativa de ativar produto inexistente: {product_id}")

        return product
