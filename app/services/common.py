from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import Type, TypeVar, Union
from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.orm import Query, Session
from math import ceil
from app.db.base_model import BaseModel
from sqlalchemy import and_, or_
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, BigInteger, func
T = TypeVar("T") 
def delete_and_refresh(db: Session, model: Type[T], id: int) -> bool:
    """
    Xóa object theo id và commit.
    Trả về True nếu xóa thành công, False nếu không tìm thấy.
    """
    deleted_count = db.query(model).filter(model.id == id).delete()
    db.commit()
    return bool(deleted_count)

def save_and_refresh(db: Session, obj: T) -> T:
    """
    Lưu 1 object vào DB, commit và refresh.
    """
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def save_all_and_refresh(db: Session, objs: list[T]) -> list[T]:
    """
    Lưu nhiều object vào DB, commit và refresh.
    """
    db.add_all(objs)
    db.commit()
    for obj in objs:
        db.refresh(obj)
    return objs

def update_and_refresh(
    db: Session,
    model: Type[T],          # class ORM model
    id: int,
    data: Union[dict, BaseModel, object]  # dict, schema, hoặc ORM object
) -> T:
    """
    Cập nhật 1 object theo id, commit và refresh.
    Cho phép data là dict, Pydantic model, hoặc ORM object.
    """

    # Nếu là ORM object (instance của model) → convert sang dict
    if isinstance(data, model):
        # Lấy tất cả column name của model
        columns = {c.name for c in model.__table__.columns}
        data = {col: getattr(data, col) for col in columns if col not in {"id", "created_at", "updated_at"}}

    # Nếu không phải dict → báo lỗi
    if not isinstance(data, dict):
        raise ValueError("data must be a dict, Pydantic model, or ORM instance")

    # Lấy object từ DB
    item = db.query(model).filter(model.id == id).first()
    if not item:
        return None

    # Gán giá trị mới
    for key, value in data.items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item


def paginate(query: Query, page: int = 1, size: int = 10):
    # Đếm tổng số record
    total_items = query.count()
    total_pages = ceil(total_items / size) if size else 1

    # Lấy dữ liệu trang hiện tại
    items = query.offset((page - 1) * size).limit(size).all()

    return {
        "data": items,
        "meta": {
            "page": page,
            "size": size,
            "total_items": total_items,
            "total_pages": total_pages
        }
    }


def paginate_cursor_by_created_at(
    query,
    model,
    time_field: str = "created_at",
    limit: int = 10,
    cursor: str | None = None,
):
    time_col = getattr(model, time_field)

    if cursor:
        cursor_time = datetime.fromisoformat(cursor)
        query = query.filter(time_col < cursor_time)

    items = (
        query
        .order_by(time_col.desc())
        .limit(limit + 1)
        .all()
    )

    has_more = len(items) > limit
    items = items[:limit]

    next_cursor = None
    if has_more:
        last = items[-1]
        next_cursor = getattr(last, time_field).isoformat().replace("+", "%2B")

    return {
        "items": items,
        "next_cursor": next_cursor,
        "has_more": has_more
    }


