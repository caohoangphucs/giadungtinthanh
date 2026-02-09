from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from .category import Category
from .common import FileInfo


class ProductMediaBase(BaseModel):
    file_id: str
    media_type: str = "image"
    position: int = 0

class ProductMediaCreate(ProductMediaBase):
    pass

class ProductMedia(ProductMediaBase):
    id: int
    file: FileInfo
    model_config = ConfigDict(from_attributes=True)

# Attribute
class VariantAttributeBase(BaseModel):
    name: str
    value: float
    unit: str

class VariantAttributeCreate(VariantAttributeBase):
    pass

class VariantAttribute(VariantAttributeBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Variant
class ProductVariantBase(BaseModel):
    price: float
    stock: int

class ProductVariantCreate(ProductVariantBase):
    attributes: List[VariantAttributeCreate] = []
    image_id: Optional[str] = None

class ProductVariantUpdate(BaseModel):
    price: Optional[float] = None
    stock: Optional[int] = None

class ProductVariant(ProductVariantBase):
    id: int
    attributes: List[VariantAttribute] = []
    image: Optional[FileInfo] = None
    model_config = ConfigDict(from_attributes=True)

# Product
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    thumbnail_id: Optional[str] = None

class ProductCreate(ProductBase):
    variants: List[ProductVariantCreate] = []
    media_ids: List[str] = [] # Simply list of file IDs for media

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    thumbnail_id: Optional[str] = None
    variants: Optional[List[ProductVariantCreate]] = None
    media_ids: Optional[List[str]] = None

class Product(ProductBase):
    id: int
    category: Optional[Category] = None
    thumbnail: Optional[FileInfo] = None
    media: List[ProductMedia] = []
    variants: List[ProductVariant] = []
    
    model_config = ConfigDict(from_attributes=True)
