"""
Repository para operações CRUD da tabela Product.
"""

from typing import Optional, List
from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

from app.models.product import Product


class ProductRepository:
    """Data access layer para Product."""

    @staticmethod
    def get_all(db: Session, active_only: bool = True) -> List[Product]:
        """
        Retorna todos os produtos.
        Usa joinedload para evitar N+1 ao carregar a Category.
        """
        query = db.query(Product).options(joinedload(Product.category))
        if active_only:
            query = query.filter(Product.active == True)
        return query.all()

    @staticmethod
    def get_by_id(db: Session, product_id: int) -> Optional[Product]:
        """Retorna um produto por ID (carrega Category com joinedload)."""
        return db.query(Product).options(joinedload(Product.category)).filter(
            Product.id == product_id
        ).first()

    @staticmethod
    def get_by_sku(db: Session, sku: str) -> Optional[Product]:
        """Retorna um produto por SKU."""
        return db.query(Product).options(joinedload(Product.category)).filter(
            Product.sku == sku
        ).first()

    @staticmethod
    def get_by_barcode(db: Session, barcode: str) -> Optional[Product]:
        """Retorna um produto por código de barras."""
        return db.query(Product).options(joinedload(Product.category)).filter(
            Product.barcode == barcode
        ).first()

    @staticmethod
    def search_by_name(db: Session, name: str, active_only: bool = True) -> List[Product]:
        """Busca produtos por nome (LIKE)."""
        query = db.query(Product).options(joinedload(Product.category)).filter(
            Product.name.ilike(f"%{name}%")
        )
        if active_only:
            query = query.filter(Product.active == True)
        return query.all()

    @staticmethod
    def get_by_category(db: Session, category_id: int, active_only: bool = True) -> List[Product]:
        """Retorna todos os produtos de uma categoria."""
        query = db.query(Product).options(joinedload(Product.category)).filter(
            Product.category_id == category_id
        )
        if active_only:
            query = query.filter(Product.active == True)
        return query.all()

    @staticmethod
    def get_low_stock(db: Session, threshold: int = 10) -> List[Product]:
        """Retorna produtos com estoque baixo."""
        return db.query(Product).options(joinedload(Product.category)).filter(
            and_(Product.active == True, Product.stock_quantity <= threshold)
        ).all()

    @staticmethod
    def create(db: Session, category_id: int, name: str, description: Optional[str],
               sku: str, barcode: Optional[str], price_cost: float, price_sale: float) -> Product:
        """Cria um novo produto."""
        product = Product(
            category_id=category_id,
            name=name,
            description=description,
            sku=sku,
            barcode=barcode,
            price_cost=price_cost,
            price_sale=price_sale,
            stock_quantity=0,
            active=True
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return db.query(Product).options(joinedload(Product.category)).filter(
            Product.id == product.id
        ).first()

    @staticmethod
    def update(db: Session, product_id: int, category_id: Optional[int] = None,
               name: Optional[str] = None, description: Optional[str] = None,
               sku: Optional[str] = None, barcode: Optional[str] = None,
               price_cost: Optional[float] = None, price_sale: Optional[float] = None,
               active: Optional[bool] = None) -> Optional[Product]:
        """Atualiza dados de um produto."""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None

        if category_id is not None:
            product.category_id = category_id
        if name is not None:
            product.name = name
        if description is not None:
            product.description = description
        if sku is not None:
            product.sku = sku
        if barcode is not None:
            product.barcode = barcode
        if price_cost is not None:
            product.price_cost = price_cost
        if price_sale is not None:
            product.price_sale = price_sale
        if active is not None:
            product.active = active

        db.commit()
        db.refresh(product)
        return db.query(Product).options(joinedload(Product.category)).filter(
            Product.id == product.id
        ).first()

    @staticmethod
    def update_stock(db: Session, product_id: int, quantity_delta: int) -> Optional[Product]:
        """
        Atualiza o estoque de um produto (somando ao valor atual).
        Pode ser negativo para saídas.
        """
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None

        product.stock_quantity += quantity_delta
        db.commit()
        db.refresh(product)
        return db.query(Product).options(joinedload(Product.category)).filter(
            Product.id == product.id
        ).first()

    @staticmethod
    def deactivate(db: Session, product_id: int) -> Optional[Product]:
        """Desativa um produto (soft delete)."""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None

        product.active = False
        db.commit()
        db.refresh(product)
        return db.query(Product).options(joinedload(Product.category)).filter(
            Product.id == product.id
        ).first()

    @staticmethod
    def activate(db: Session, product_id: int) -> Optional[Product]:
        """Ativa um produto desativado."""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None

        product.active = True
        db.commit()
        db.refresh(product)
        return db.query(Product).options(joinedload(Product.category)).filter(
            Product.id == product.id
        ).first()
