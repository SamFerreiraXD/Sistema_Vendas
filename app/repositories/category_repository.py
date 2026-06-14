"""
Repository para operações CRUD da tabela Category.
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.product import Category


class CategoryRepository:
    """Data access layer para Category."""

    @staticmethod
    def get_all(db: Session) -> List[Category]:
        """Retorna todas as categorias."""
        return db.query(Category).all()

    @staticmethod
    def get_by_id(db: Session, category_id: int) -> Optional[Category]:
        """Retorna uma categoria por ID."""
        return db.query(Category).filter(Category.id == category_id).first()

    @staticmethod
    def get_by_slug(db: Session, slug: str) -> Optional[Category]:
        """Retorna uma categoria por slug."""
        return db.query(Category).filter(Category.slug == slug).first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Category]:
        """Retorna uma categoria por nome."""
        return db.query(Category).filter(Category.name == name).first()

    @staticmethod
    def create(db: Session, name: str, slug: str, description: Optional[str] = None) -> Category:
        """Cria uma nova categoria."""
        category = Category(
            name=name,
            slug=slug,
            description=description
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def update(db: Session, category_id: int, name: Optional[str] = None,
               slug: Optional[str] = None, description: Optional[str] = None) -> Optional[Category]:
        """Atualiza uma categoria."""
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return None

        if name is not None:
            category.name = name
        if slug is not None:
            category.slug = slug
        if description is not None:
            category.description = description

        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def delete(db: Session, category_id: int) -> bool:
        """Deleta uma categoria (e seus produtos se houver cascade)."""
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return False

        db.delete(category)
        db.commit()
        return True
