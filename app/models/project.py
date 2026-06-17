from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class Project(Base):
    __tablename__ = "project"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=False)
    description = Column(String(255), nullable=False)
    created_at = Column(Date, nullable=False)

    documents = relationship(
        "Document",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name!r}, description={self.description!r}, created_at={self.created_at!r})>"
