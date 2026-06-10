from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repository.user import UserRepository
from app.services.user import UserService


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    repository = UserRepository(db)
    return UserService(repository)
