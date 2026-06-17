from sqlalchemy.orm import Session

from app.models.user import User
from app.repository.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(db, User)

    def get_user_by_id(self, user_id: int) -> User:
        return self.get_by_id(user_id)

    def get_user_by_email(self, email: str) -> User:
        return self.db.query(self.model).filter(self.model.email == email).first()

    def create_user(self, *, email: str, hashed_password: str):
        return self.create(email=email, hashed_password=hashed_password)
