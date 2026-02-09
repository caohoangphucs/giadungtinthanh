from sqlalchemy.orm import Session, joinedload
from app.models.product import Product, ProductVariant, VariantAttribute, Category, ProductMedia
from app.schemas.product import ProductCreate, ProductUpdate, ProductVariantCreate

class ProductService:
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100, name: str = None, category_id: int = None):
        query = db.query(Product)
        
        if name:
            query = query.filter(Product.name.ilike(f"%{name}%"))
        
        if category_id:
            query = query.filter(Product.category_id == category_id)

        return query.options(
            joinedload(Product.thumbnail),
            joinedload(Product.media).joinedload(ProductMedia.file),
            joinedload(Product.variants).joinedload(ProductVariant.attributes),
            joinedload(Product.category)
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_category_slug(db: Session, slug: str, skip: int = 0, limit: int = 100):
        return db.query(Product).join(Product.category).options(
            joinedload(Product.thumbnail),
            joinedload(Product.media).joinedload(ProductMedia.file),
            joinedload(Product.variants).joinedload(ProductVariant.attributes),
            joinedload(Product.category)
        ).filter(Category.slug == slug).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, product_id: int):
        return db.query(Product).options(
            joinedload(Product.thumbnail),
            joinedload(Product.media).joinedload(ProductMedia.file),
            joinedload(Product.variants).joinedload(ProductVariant.attributes),
            joinedload(Product.category)
        ).filter(Product.id == product_id).first()

    @staticmethod
    def create(db: Session, product_in: ProductCreate):
        # Create Product
        db_product = Product(
            name=product_in.name,
            description=product_in.description,
            category_id=product_in.category_id,
            thumbnail_id=product_in.thumbnail_id
        )
        db.add(db_product)
        db.flush() # Get product ID

        # Create Media
        for idx, file_id in enumerate(product_in.media_ids):
            db_media = ProductMedia(
                product_id=db_product.id,
                file_id=file_id,
                position=idx
            )
            db.add(db_media)

        # Create Variants
        for v_in in product_in.variants:
            db_variant = ProductVariant(
                product_id=db_product.id,
                price=v_in.price,
                stock=v_in.stock
            )
            db.add(db_variant)
            db.flush() # Get variant ID
            
            # Create Attributes
            for a_in in v_in.attributes:
                db_attr = VariantAttribute(
                    variant_id=db_variant.id,
                    name=a_in.name,
                    value=a_in.value,
                    unit=a_in.unit
                )
                db.add(db_attr)

        db.commit()
        db.refresh(db_product)
        return db_product

    @staticmethod
    def update(db: Session, product_id: int, product_in: ProductUpdate):
        db_product = ProductService.get_by_id(db, product_id)
        if not db_product:
            return None
        
        update_data = product_in.model_dump(exclude_unset=True)
        
        # Handle variants if provided
        if "variants" in update_data:
            variants_data = update_data.pop("variants")
            # Delete old variants
            db.query(ProductVariant).filter(ProductVariant.product_id == product_id).delete()
            # Create new variants
            for v_in in variants_data:
                db_variant = ProductVariant(
                    product_id=product_id,
                    price=v_in["price"],
                    stock=v_in["stock"]
                )
                db.add(db_variant)
                db.flush()
                for a_in in v_in.get("attributes", []):
                    db_attr = VariantAttribute(
                        variant_id=db_variant.id,
                        name=a_in["name"],
                        value=a_in["value"],
                        unit=a_in["unit"]
                    )
                    db.add(db_attr)

        # Handle media if provided
        if "media_ids" in update_data:
            media_ids = update_data.pop("media_ids")
            # Delete old media associations
            db.query(ProductMedia).filter(ProductMedia.product_id == product_id).delete()
            # Create new media associations
            for idx, file_id in enumerate(media_ids):
                db_media = ProductMedia(
                    product_id=product_id,
                    file_id=file_id,
                    position=idx
                )
                db.add(db_media)

        # Update other fields
        for field, value in update_data.items():
            setattr(db_product, field, value)
            
        db.commit()
        db.refresh(db_product)
        return db_product

    @staticmethod
    def delete(db: Session, product_id: int):
        db_product = ProductService.get_by_id(db, product_id)
        if not db_product:
            return False
        
        db.delete(db_product)
        db.commit()
        return True
