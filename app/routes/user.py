from typing import List

from fastapi import status
from fastapi.security import OAuth2PasswordBearer

from fastapi import APIRouter, Depends

from app.schemas.user import *
from app.security import password
from app.services.user import UserService, get_user_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserResponse], summary="List users")
def read_users(user_service: UserService = Depends(get_user_service)):
    """Listar todos los usuarios."""
    return user_service.list_users()

@router.post("/create-user", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Crear usuario")
def create_user(
    user: UserCreate,
    user_service: UserService = Depends(get_user_service)):
    """Crear un nuevo usuario."""
    return user_service.create_user(user)

@router.get("/id/{user_id}", response_model=UserResponse, summary="Obtener usuario por ID")
def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service)):
    """Obtener un usuario por su ID."""
    return user_service.get_user(user_id)

@router.post("/login", summary="Iniciar sesión")
def login(
    user_login: UserLogin, 
    user_service: UserService = Depends(get_user_service)):
    """Iniciar sesión con email y contraseña, devuelve un token JWT."""
    return user_service.login(user_login.email, user_login.password)

@router.get("/hello", summary="Saludar con token")
def say_hello(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)):
    """Saludar en consola solo si el token es válido."""
    user_service.say_hello(token)
    return {"message": "Hello! Your token is valid."}