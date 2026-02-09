from app.core.config import settings
from app.db.session import SessionLocal
from fastapi import Cookie, HTTPException, status
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
SECRET = settings.SECRET
oauth2_scheme = HTTPBearer()

def require_admin(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    if token.credentials != SECRET:
        raise HTTPException(404, "Login please :))")

    return "OK"
  
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
