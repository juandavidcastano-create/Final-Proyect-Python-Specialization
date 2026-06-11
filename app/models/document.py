from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base

class Document(Base):
    __tablename__ = "document"
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String(255), nullable=False)
    dir = Column(String(255), nullable=False)
    size = Column(Integer, nullable=False)
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"), nullable=False)

    project = relationship("Project", back_populates="documents")

    def __repr__(self):
        return f"<Document(id={self.id}, file_name={self.file_name!r}, dir={self.dir!r}, size={self.size}, project_id={self.project_id})>"