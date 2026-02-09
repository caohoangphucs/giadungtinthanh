from sqlalchemy import Text, String, ForeignKey, DateTime, Float, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base_model import BaseModel
from enum import Enum
from app.enums.general import *
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, BigInteger
from sqlalchemy.sql import func
from app.db.base import Base