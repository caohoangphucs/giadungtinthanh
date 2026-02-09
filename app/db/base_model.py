from sqlalchemy import Column, BigInteger, DateTime, func
from app.db.base import Base

class BaseModel(Base):
    __abstract__ = True

    id = Column(BigInteger, primary_key=True, index=True)
    create_at = Column(DateTime(timezone=True), server_default=func.now())
    update_at = Column(DateTime(timezone=True), onupdate=func.now())
    creator_id = Column(BigInteger)
