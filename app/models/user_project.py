from sqlalchemy import Column, ForeignKey, Integer, String

from app.db.database import Base


class UserProject(Base):
    __tablename__ = "user_project"
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    project_id = Column(Integer, ForeignKey("project.id"), primary_key=True)
    role = Column(String(10), nullable=False)

    def __repr__(self):
        return f"<UserProject(user_id={self.user_id}, project_id={self.project_id}, role={self.role!r})>"
    
