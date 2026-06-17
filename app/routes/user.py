from fastapi import status
from fastapi.security import OAuth2PasswordBearer

from fastapi import APIRouter, Depends

from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.user import UserService
from app.dependencies.user import get_user_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/auth", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Crear usuario")
def create_user(
    user: UserCreate,
    user_service: UserService = Depends(get_user_service)):
    """Crear un nuevo usuario."""
    return user_service.create_user(user)

@router.post("/login", summary="Iniciar sesión")
def login(
    user_login: UserLogin, 
    user_service: UserService = Depends(get_user_service)):
    """Iniciar sesión con email y contraseña, devuelve un token JWT."""
    return user_service.login(user_login.email, user_login.password)
