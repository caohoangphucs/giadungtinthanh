from pydantic import BaseModel, ConfigDict
from typing import Optional
from .common import FileInfo

class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    thumbnail_id: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    thumbnail_id: Optional[str] = None

class Category(CategoryBase):
    id: int
    thumbnail: Optional[FileInfo] = None
    
    model_config = ConfigDict(from_attributes=True)
