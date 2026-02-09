from sqlalchemy.orm import Session, joinedload
from app.models.product import Category
from app.schemas.category import CategoryCreate, CategoryUpdate

class CategoryService:
    @staticmethod
    def get_all(db: Session):
        return db.query(Category).options(joinedload(Category.thumbnail)).all()

    @staticmethod
    def get_by_id(db: Session, category_id: int):
        return db.query(Category).options(joinedload(Category.thumbnail)).filter(Category.id == category_id).first()

    @staticmethod
    def get_by_slug(db: Session, slug: str):
        return db.query(Category).options(joinedload(Category.thumbnail)).filter(Category.slug == slug).first()

    @staticmethod
    def create(db: Session, category_in: CategoryCreate):
        db_category = Category(
            name=category_in.name,
            slug=category_in.slug,
            description=category_in.description,
            thumbnail_id=category_in.thumbnail_id
        )
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category

    @staticmethod
    def update(db: Session, category_id: int, category_in: CategoryUpdate):
        db_category = CategoryService.get_by_id(db, category_id)
        if not db_category:
            return None
        
        update_data = category_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)
            
        db.commit()
        db.refresh(db_category)
        return db_category

    @staticmethod
    def delete(db: Session, category_id: int):
        db_category = CategoryService.get_by_id(db, category_id)
        if not db_category:
            return False
        
        db.delete(db_category)
        db.commit()
        return True
