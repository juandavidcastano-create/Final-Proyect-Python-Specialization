from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repository.user import UserRepository
from app.security.password import hash_password, verify_password
from app.dependencies.auth import create_access_token, decode_access_token
from app.schemas.user import UserCreate


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def list_users(self):
        return self.repository.list_users()

    def get_user(self, user_id: int):
        return self.repository.get_user_by_id(user_id)

    def create_user(self, user_create: UserCreate):
        # Ensure repeated password matches
        if user_create.password != user_create.repeated_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match",
            )

        if self.repository.get_user_by_email(user_create.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Hash the confirmed password and persist only the hashed value
        hashed_password = hash_password(user_create.password)
        return self.repository.create_user(
            email=user_create.email,
            hashed_password=hashed_password,
        )

    def login(self, email: str, password: str) -> str:
        """Verify email and password, return JWT token on success."""
        user = self.repository.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_data = {"sub": user.email, "user_id": user.id}
        access_token = create_access_token(token_data)
        return access_token

    def say_hello(self, token: str) -> None:
        """Print greeting to console only if token is valid."""
        try:
            payload = decode_access_token(token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Token is valid
        print("hola estoy loggeado")



def get_user_service(db: Session = Depends(get_db)) -> UserService:
    repository = UserRepository(db)
    return UserService(repository)
