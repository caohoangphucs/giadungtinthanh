from sqlalchemy import (
    String,
    Text,
    Numeric,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base
from app.models.file import File


# =========================
# Category
# =========================
class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    
    thumbnail_id: Mapped[str | None] = mapped_column(
        ForeignKey("files.id", ondelete="SET NULL"),
        nullable=True
    )
    thumbnail: Mapped["File"] = relationship()

    products: Mapped[list["Product"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan"
    )


# =========================
# Product (sản phẩm gốc)
# =========================
class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    category: Mapped["Category"] = relationship(
        back_populates="products"
    )

    thumbnail_id: Mapped[str | None] = mapped_column(
        ForeignKey("files.id", ondelete="SET NULL"),
        nullable=True
    )
    thumbnail: Mapped["File"] = relationship(
        foreign_keys=[thumbnail_id]
    )

    media: Mapped[list["ProductMedia"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan"
    )

    variants: Mapped[list["ProductVariant"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan"
    )


# =========================
# Product Media
# =========================
class ProductMedia(Base):
    __tablename__ = "product_media"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )
    file_id: Mapped[str] = mapped_column(
        ForeignKey("files.id", ondelete="CASCADE"),
        nullable=False
    )
    media_type: Mapped[str] = mapped_column(String(20), default="image") # image, video
    position: Mapped[int] = mapped_column(Integer, default=0)

    product: Mapped["Product"] = relationship(back_populates="media")
    file: Mapped["File"] = relationship()


# =========================
# Product Variant
# (size / dung lượng / phiên bản)
# =========================
class ProductVariant(Base):
    __tablename__ = "product_variants"

    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )

    price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    stock: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    image_id: Mapped[str | None] = mapped_column(
        ForeignKey("files.id", ondelete="SET NULL"),
        nullable=True
    )
    image: Mapped["File"] = relationship()

    product: Mapped["Product"] = relationship(
        back_populates="variants"
    )

    attributes: Mapped[list["VariantAttribute"]] = relationship(
        back_populates="variant",
        cascade="all, delete-orphan"
    )


# =========================
# Variant Attribute
# (width, height, capacity...)
# =========================
class VariantAttribute(Base):
    __tablename__ = "variant_attributes"

    id: Mapped[int] = mapped_column(primary_key=True)

    variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants.id", ondelete="CASCADE"),
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    value: Mapped[float] = mapped_column(
        Numeric(12, 4),
        nullable=False
    )

    unit: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    variant: Mapped["ProductVariant"] = relationship(
        back_populates="attributes"
    )
