from .common import *
router = APIRouter(prefix="/api/auth", tags=["Auth"])
from app.core.dependencies import *
ADMIN_USERNAME = settings.ADMIN_USER
ADMIN_PASSWORD = settings.ADMIN_PASSWORD
ADMIN_TOKEN = settings.SECRET


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def admin_login(data: LoginRequest, request: Request, response: Response):
    if (
        data.username != ADMIN_USERNAME
        or data.password != ADMIN_PASSWORD
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"access_token": ADMIN_TOKEN}


@router.get("/me")
def test(
    auth = Depends(require_admin)
):
    return {
        "Ok":True,
        "Role":"admin",
        "user": ADMIN_USERNAME
    }