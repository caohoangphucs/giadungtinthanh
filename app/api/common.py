from fastapi import APIRouter, Response, HTTPException, Request
from pydantic import BaseModel
from app.core.config import settings
from app.core.dependencies import require_admin
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from app.core.dependencies import get_db

