import importlib
import pkgutil
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import *
from app.models import *

from fastapi import Query
from pydantic import BaseModel

def _autodiscover(package_name: str = __name__, router = APIRouter):
    package = importlib.import_module(package_name)
    for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
        if is_pkg:
            continue
        full_name = f"{package_name}.{module_name}"
        module = importlib.import_module(full_name)
        if hasattr(module, "router"):
            router.include_router(module.router)

router = APIRouter()
_autodiscover(__name__, router)