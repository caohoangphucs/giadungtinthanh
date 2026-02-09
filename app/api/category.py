from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.services.category_service import CategoryService
from app.schemas.category import Category, CategoryCreate, CategoryUpdate
from app.core.dependencies import get_db

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("/", response_model=List[Category])
def list_categories(db: Session = Depends(get_db)):
    return CategoryService.get_all(db)

@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(category_in: CategoryCreate, db: Session = Depends(get_db)):
    # Check if slug exists
    if CategoryService.get_by_slug(db, category_in.slug):
        raise HTTPException(status_code=400, detail="Slug already exists")
    return CategoryService.create(db, category_in)

@router.get("/{category_id}", response_model=Category)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = CategoryService.get_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.get("/slug/{slug}", response_model=Category)
def get_category_by_slug(slug: str, db: Session = Depends(get_db)):
    category = CategoryService.get_by_slug(db, slug)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.put("/{category_id}", response_model=Category)
def update_category(category_id: int, category_in: CategoryUpdate, db: Session = Depends(get_db)):
    category = CategoryService.update(db, category_id, category_in)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    if not CategoryService.delete(db, category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}
