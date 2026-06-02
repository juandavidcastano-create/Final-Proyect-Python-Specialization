from sqlalchemy import Column, Integer, String

from app.db.database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), nullable=False, unique=True)
    hashed_password = Column(String(150), nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email!r}, hashed_password={self.hashed_password!r})>"
